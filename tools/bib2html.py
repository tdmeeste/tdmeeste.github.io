#quick hacking...
#some definitions originate from https://bitbucket.org/wkjarosz/academic-website-tools/


import pybtex.database.input.bibtex
import pybtex.database.output.bibtex
from unidecode import unidecode
#import latexcodec
import html
from pylatexenc.latex2text import LatexNodes2Text
from bs4 import BeautifulSoup
import os

bibfolder = 'bib'
#bibfile_EE = os.path.join(bibfolder, 'TD_electrical_engineering.bib')
#bibfile_CS = os.path.join(bibfolder, 'TD_computer_science.bib')
#bibfile_2021 = os.path.join(bibfolder, '2021.bib')
#bibfile_2022 = os.path.join(bibfolder, '2022.bib')
#bibfile_2023 = os.path.join(bibfolder, '2023.bib')
#bibfile_2024 = os.path.join(bibfolder, '2024.bib')


#bibfiles = [("EE", bibfile_EE), ("CS", bibfile_CS)]
bibfiles = [os.path.join(bibfolder, f) for f in os.listdir(bibfolder) if f.endswith('.bib')]


def strip_braces(s):
    return s.replace("{", u'').replace("}", u'')


def latex_to_unicode(s):
    s = LatexNodes2Text().latex_to_text(s)
    # import latexcodec
    # return codex.decode(strip_braces(s), "ulatex+utf8")
    return strip_braces(s)


def unicode_to_html(s):
    return html.escape(s)
    # return s.encode('ascii', 'xmlcharrefreplace')


def latex_to_html(s):
    return unicode_to_html(latex_to_unicode(s))


def person_name(person):
    name = ' '.join(
        person.first_names + person.middle_names + person.prelast_names + person.last_names + person.lineage_names)
    name = latex_to_unicode(name)
    return name

def is_me(author):
    return 'thomas' in author.lower() and 'demeester' in author.lower()


def get_venue(bibentry):
    if bibentry.type == 'article':
        return latex_to_unicode(bibentry.fields['journal'])
    elif bibentry.type == 'inproceedings':
        return latex_to_unicode(bibentry.fields['booktitle'])
    elif bibentry.type == 'proceedings':
        return latex_to_unicode(bibentry.fields['series'])
    elif bibentry.type == 'phdthesis':
        return u'Ph.D. Dissertation, %s' % latex_to_unicode(bibentry.fields['school'])
    elif bibentry.type == 'thesis':
        return u'%s, %s' % (latex_to_unicode(bibentry.fields['type']), latex_to_unicode(bibentry.fields['school']))
    elif bibentry.type == 'techreport':
        return u'Tech. Report, %s' % latex_to_unicode(bibentry.fields['institution'])
    elif bibentry.type == 'patent':
        return u'Patent, %s %s' % (
        latex_to_unicode(bibentry.fields['location']), latex_to_unicode(bibentry.fields['number']))
    elif bibentry.type == 'misc':
        return latex_to_unicode(bibentry.fields['howpublished'])



def format_entry(bibentry):
    # quick & dirty

    bibtype = bibentry.type.lower()
    if bibtype in ['inproceedings', 'article', 'phdthesis']:
        # authors
        authors_string, author_key = "", ""
        if 'author' in bibentry.persons:
            author_key = 'author'
        elif 'editor' in bibentry.persons:
            author_key = 'editor'
        if len(author_key) > 0:
            authors_lst = [unidecode(person_name(author)) for author in bibentry.persons[author_key]]
            authors_lst = [author if not is_me(author) else '<u>' + author + '</u>' for author in authors_lst]
            authors_string = ', '.join(authors_lst)

        """
        author_key = 'author' if 'author' in bibentry.persons
            author_key =
            # authors_string = unidecode(u', '.join([person_name(author) for author in bibentry.persons['author']]))
            authors_string = u', '.join([person_name(author) for author in bibentry.persons['author']])
        elif 'editor' in bibentry.persons:
            authors_string = unidecode(u', '.join([person_name(editor) for editor in bibentry.persons['editor']]))
        """
        # title
        title_string = "" if not 'title' in bibentry.fields else unidecode(strip_braces(bibentry.fields['title']))
        # venue / journal
        target_string = get_venue(bibentry)
        # year
        year_string = "" if not 'year' in bibentry.fields else unidecode(bibentry.fields['year'])

        # online
        online = ""
        if 'url' in bibentry.fields and not 'doi.' in bibentry.fields['url']:
            online += '&nbsp;<a href="{}">[online]</a>'.format(bibentry.fields['url'])
        if 'code' in bibentry.fields:
            online += '&nbsp;<a href="{}">[code]</a>'.format(bibentry.fields['code'])
        if 'data' in bibentry.fields:
            online += '&nbsp;<a href="{}">[data]</a>'.format(bibentry.fields['data'])
        if 'misc' in bibentry.fields:
            online += '&nbsp;{}'.format(bibentry.fields['misc'])
        if 'pdf' in bibentry.fields:
            online += '&nbsp;<a href="{}">[pdf]</a>'.format(bibentry.fields['pdf'])
        if 'slides' in bibentry.fields:
            online += '&nbsp;<a href="{}">[slides]</a>'.format(bibentry.fields['slides'])
        if 'status' in bibentry.fields:
            online += '&nbsp;<b><font color="blue">({})</font></b>'.format(bibentry.fields['status'])


        #pubtype
        pubtype = ""
        if 'pubtype' in bibentry.fields:
            if bibentry.fields['pubtype'] == 'a1':
                pubtype += '&nbsp;<b><font color="green">(a1)</font></b>'

        result = '\t<li>'
        result += authors_string + '. ' if len(authors_string) > 0 else ''
        result += '&nbsp;<i>"' + unicode_to_html(title_string.strip()) + '"</i>' if len(title_string) > 0 else ''
        result += ',&nbsp;<b>' + unicode_to_html(target_string) + '</b>' if len(target_string) > 0 else ''
        result += ',&nbsp;' + unicode_to_html(year_string) + '.' if len(year_string) > 0 else '.'
        result += online
        result += pubtype
        result += '</li>'



    else:
        result = ''
        print('entry of type', bibtype, 'not included yet.')

    return result


def format_year(yyyy, domain=''):
    result = '<a name=bib{}{}></a>'.format(domain, yyyy)
    result += '<div class="column top-vspace05"><header><h3>{}</h3></header></div>'.format(yyyy)
    return result


#write a loop over all bib files, first storing them in a list, obtaining the year, and then writing the html file, ordered by year from newest to oldest:
total_a1 = 0
bib_items = []
for bibfile in bibfiles:
    # Load the list of publications from bib file
    parser = pybtex.database.input.bibtex.Parser(encoding="UTF-8")
    bib_data = parser.parse_file(bibfile)
    bib_items.extend([bibentry for id, bibentry in bib_data.entries.items()])

print('found', len(bib_items), 'entries in total')
bib_items_per_year = {}
for bibentry in bib_items:
    if not 'year' in bibentry.fields:
        print('\nWarning: no "year" field - ignore entry \n', bibentry)
    else:
        year = int(''.join([c for c in bibentry.fields['year'] if c.isdigit()]))
        if year not in bib_items_per_year:
            bib_items_per_year[year] = []
        bib_items_per_year[year].append(bibentry)

for year in bib_items_per_year:
    print(year)
    #for bib_entry in bib_items_per_year[year]:
    #    print(bib_entry)


#convert to html
pybtex_html_backend = pybtex.plugin.find_plugin('pybtex.backends', 'html')()
html_str = ""
sorted_years = sorted(bib_items_per_year.keys(), reverse=True)
for year in sorted_years:
    html_str += '\n' + format_year(year)
    html_str += '\n<div class="column"><ul class="alt">'

    for bibentry in bib_items_per_year[year]:
        if 'pubtype' in bibentry.fields and bibentry.fields['pubtype'] == 'a1':
            total_a1 += 1

        entry_html = format_entry(bibentry)
        html_str += '\n' + entry_html

    html_str += '\n</ul></div>'

with open('_includes/biblio_all.html', 'w') as htmlfile:
    htmlfile.write(html_str)
    print('wrote', '_includes/biblio_all.html')











# total_a1 = 0
# for domain, bibfile in bibfiles:
#     # Load the list of publications from bib file
#     parser = pybtex.database.input.bibtex.Parser(encoding="UTF-8")

#     bib_data = parser.parse_file(bibfile)

#     pybtex_html_backend = pybtex.plugin.find_plugin('pybtex.backends', 'html')()

#     html_str = ""

#     current_year = 2100
#     is_first = True

#     for id, bibentry in bib_data.entries.items():
#         if 'pubtype' in bibentry.fields and bibentry.fields['pubtype'] == 'a1':
#             total_a1 += 1

#         if not 'year' in bibentry.fields:
#             print('\nWarning: no "year" field - ignore entry \n', bibentry)
#         else:
#             year = int(bibentry.fields['year'])
#             if year > current_year:
#                 print('\nWarning: invalid "year" field - make sure input bib file ordered from newest to oldest.')
#                 print('ignore entry \n', bibentry)
#                 #assume ordered from newest to oldest
#             elif year < current_year:
#                 #close unordered list if not first
#                 if is_first:
#                     is_first = False
#                 else:
#                     html_str += '\n</ul></div>'

#                 #add new year
#                 year_html = format_year(year, domain)
#                 html_str += '\n' + year_html
#                 current_year = year
#                 #open new unordered list
#                 html_str += '\n<div class="column"><ul class="alt">'

#             #own formatting for simplicity
#             entry_html = format_entry(bibentry)
#             html_str += '\n' + entry_html

#     #at end: close div and ul
#     html_str += '\n</ul></div>'


#     with open('_includes/biblio_%s.html' % domain, 'w') as htmlfile:
#         htmlfile.write(html_str)
#         print('wrote', '_includes/biblio_%s.html' % domain)
# #        htmlfile.write(BeautifulSoup(html_str, 'html.parser').prettify())

print('total a1 papers: ', total_a1)