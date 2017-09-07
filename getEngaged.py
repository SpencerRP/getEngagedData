from bs4 import BeautifulSoup
import requests
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
    resulting_json = dict()
    soup = BeautifulSoup(staff_report_html, 'html.parser')
    print(soup.title)


for table in soup.findChildren('table', {'class': 'agendaTable'}):
    rows = table.findChildren(['tr'])
    for row in rows:
        cells = row.findChildren('td')
        date = cells[0].string
        links = []
        for link in cells[1].findChildren('a', {'href': True}):
            links.append(link['href'])
        if cells[1].string == "Agenda":
            agenda = requests.get(links[0]).text
            if ("CONSENT CALENDAR" in agenda):
                soup_agenda = BeautifulSoup(agenda, 'html.parser')
                tableMeeting = soup_agenda.findChild(
                    'table', {'id': 'MeetingDetail'})
                rowsMeeting = tableMeeting.findChildren(['tr'])
                i = 0
                temp = ""
                while "CLOSED" not in temp:
                    if (rowsMeeting[i].contents[1].strong != None):
                        temp = rowsMeeting[i].contents[1].strong.string
                    i += 1
                while "SPECIAL" not in temp:
                    if (rowsMeeting[i].contents[1].strong != None):
                        temp = rowsMeeting[i].contents[1].strong.string
                    linksMeeting = rowsMeeting[i].findChild(
                        'a', {'href': True})
                    full_url = "http://santamonicacityca.iqm2.com/Citizens/" + \
                        linksMeeting['href']
                    print full_url
                    staff_report_r = requests.get(
                        full_url)
                    content = process_staff_report(staff_report_r.text)
                    i += 1
