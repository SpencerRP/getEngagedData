from bs4 import BeautifulSoup
import requests
import json
import io

city_council_agendas_url = "https://www.smgov.net/departments/clerk/agendas.aspx"
r = requests.get(city_council_agendas_url)
soup = BeautifulSoup(r.text, 'html.parser')

agendas = dict()


def process_staff_report(staff_report_html):
    '''
    staff_report_html is the HTML text

    returns resulting_json which is a dictionary with keys:
        sponsors,
    '''
    staff_report_soup = BeautifulSoup(
        staff_report_html, 'html.parser')
    title = staff_report_soup.find(
        'div', {'class': 'LegiFileTitle'})
    if title != None:
        title = title.h1.string
    info = staff_report_soup.find(
        'div', {'class': 'LegiFileInfo'})
    info_dict = dict()
    info_dict['title'] = title
    if info != None:
        info_rows = info.div.table.find_all(
            ['tr'])
        for info_row in info_rows:
            info_headers = info_row.find_all(
                'th')
            info_values = info_row.find_all(
                'td')
            for i in enumerate(info_headers):
                info_dict[i[1].strong.string] = info_values[i[0]].string
    discussion = staff_report_soup.find(
        'div', {'id': 'divItemDiscussion'})
    if discussion != None:
        recommendations = discussion.div.div.find_all(
            'p')
        recommandations_text = []
        for recommendation in enumerate(recommendations):
            text_recommendation = ""
            if recommendation[0] < 2:
                continue
            spans = recommendation[1].find_all(
                'span')
            for span in enumerate(spans):
                if span[0] < 1:
                    continue
                text_recommendation += span[1].text
            recommandations_text.append(
                text_recommendation)
        info_dict['recommendations'] = recommandations_text
    body = staff_report_soup.find(
        'div', {'id': 'divBody'})
    if body != None:
        body_paragraphs = {}
        paragraphs = body.div.div.find_all('p')
        subject = ""
        content = ""
        for paragraph in paragraphs:
            spans = paragraph.find_all('span')
            if (len(spans) == 1) and 'bold' in spans[0].attrs['style']:
                if content != "" and subject != "other":
                    body_paragraphs[subject] = content
                elif subject == "other":
                    if body_paragraphs.has_key(subject):
                        body_paragraphs[subject] += content
                    else:
                        body_paragraphs[subject] = content
                content = ""
                if "Summary" in spans[0].text:
                    subject = "summary"
                elif "Background" in spans[0].text:
                    subject = "background"
                else:
                    subject = "other"
            else:
                for span in spans:
                    content += span.text
        info_dict['body'] = body_paragraphs
    return info_dict


table = soup.find('table', {'class': 'agendaTable'})
rows = table.findAll('tr')
for row in rows:
    print(row)
    cells = row.findChildren('td')
    date = cells[0].string
    links = []
    for link in cells[1].findChildren('a', {'href': True}):
        links.append(link['href'])
    if cells[1].string == "Agenda":
        agenda = requests.get(links[0]).text
        if "CONSENT CALENDAR" in agenda:
            # Searches the entire HTML text for the words since it's not yet parsed into html by BS
            soup_agenda = BeautifulSoup(agenda, 'html.parser')
            tableMeeting = soup_agenda.find(
                'table', {'id': 'MeetingDetail'})
            string_sections = tableMeeting.find_all(
                'strong')
            parent = string_sections[0].find_parent("tr")
            next_siblings = parent.find_next_siblings("tr")
            print(next_siblings)
            staff_reports = []
            reports_holder = []
            for sibling in enumerate(next_siblings):
                if (sibling[1].find('strong') == None):
                    cells = sibling[1].find_all('td')
                    if len(cells) > 2 and u'Title' in cells[2]['class']:
                        staff_report = cells[2].find(
                            'a', {'href': True})
                        if staff_report is None:
                            continue
                        staff_report_href = 'http://santamonicacityca.iqm2.com/Citizens/' + \
                            staff_report['href']
                        staff_report_r = requests.get(
                            staff_report_href)
                        staff_report_html = staff_report_r.text.encode(
                            'ascii', 'ignore').decode('ascii')
                        reports_holder.append(
                            process_staff_report(staff_report_html))
                else:
                    staff_reports.append(reports_holder)
                    reports_holder = []
            agendas[date] = staff_reports
    with io.open('temp', 'w', encoding='utf-8') as temp:
        s = json.dumps(agendas, ensure_ascii=False)
        temp.write(unicode(s))
