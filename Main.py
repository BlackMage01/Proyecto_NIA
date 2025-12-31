import feedparser
import datetime
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from datetime import datetime


# Feeds de interés: 
''' Specific RSS urls (these are the equivalent to an XML made link) '''

AP_news_url = "https://news.google.com/rss/search?q=https%3A%2F%2Fapnews.com%2Fnoticias&hl=es-419&gl=US&ceid=US%3Aes-419" #AP news google news funnel
Reuters_url = "https://news.google.com/rss/search?q=latin%20america%20site%3Ahttps%3A%2F%2Fwww.reuters.com%2Fworld%2Famericas&hl=es-419&gl=US&ceid=US%3Aes-419" #Reuters Americas - Needs translation - google news funnel
Inforbae_url = "https://news.google.com/rss/search?q=site%3Ahttps%3A%2F%2Fwww.infobae.com%2Famerica&hl=es-419&gl=US&ceid=US%3Aes-419" # Infobae google news funnel

scrap_list = [AP_news_url,Reuters_url,Inforbae_url]

#Genera una lista de diccionarios y cada elemento funciona como una pieza individual de un html.
def scrape_article(target_url):
    show_list = [] #Lista de artículos funcionales en la página
    try:
        print(f"Obteniendo feed desde {target_url}. . .")
        feed = feedparser.parse(target_url)

        if feed.bozo:
            print(f"Feed parsing error (recovered): {feed.bozo_exception}")
        print(f"Found {len(feed.entries)} entries")
        

        source_names = {
            AP_news_url: "AP News",
            Reuters_url: "Reuters",
            Inforbae_url: "Infobae"
        }

        day_names = {
            "Mon": "Lun",
            "Tue": "Mar",
            "Wed": "Mie",
            "Thu": "Jue",
            "Fri": "Vie",
            "Sat": "Sab",
            "Sun": "Dom"
        }

        month_names = {
            "Jan": "Ene",
            "Feb": "Feb",
            "Mar": "Mar",
            "Apr": "Abr",
            "May": "May",
            "Jun": "Jun",
            "Jul": "Jul",
            "Aug": "Ago",
            "Sep": "Sep",
            "Oct": "Oct",
            "Nov": "Nov",
            "Dec": "Dec",
        }

        for entry in feed.entries[:10]:
            title = entry.title #Busca especificamente artículos de reuters
            if target_url == Reuters_url:
                try:
                    title = GoogleTranslator(source='auto', target='es').translate(title)
                    print(f"Translated title: {title}")  # Debug: Print translated title
                except Exception as e:
                    print(f"Translation failed for {title}: {e}")
                    #En caso de fallo usa el título original
                    pass
            
            #Modifica pubDate a la fecha en español.
            pub_date_full = entry.published if hasattr(entry, 'published') else entry.get('pubDate', '')
            if pub_date_full:
                try:
                    pub_date = datetime.strptime(pub_date_full, "%a, %d %b %Y %H:%M:%S %Z")

                    day_abbr = pub_date.strftime("%a")
                    month_abbr = pub_date.strftime("%b")
                    
                    trans_day = day_names.get(day_abbr, day_abbr)
                    trans_month = month_names.get(month_abbr, month_abbr)

                    trans_pub_date = f"{trans_day}, {pub_date.day} {trans_month} {pub_date.year} {pub_date.strftime('%H:%M')}"
                    
                    show_list.append({
                        "title": title,
                        "link": entry.link,
                        "source": source_names.get(target_url, "Unknown"), #Extraer nombre de fuente de la url
                        "date": trans_pub_date, #Fecha y hora de publicación traducida (es)
                        "datetime_sort": pub_date
                    })   
                except ValueError as e:
                    print(f"Error parsing date for entry: {e}")
                    # Fallback to current date if parsing fails
                    pub_date = datetime.now()
                    translated_pub_date = pub_date.strftime("%Y-%m-%d %H:%M")
                    show_list.append({
                        "title": title,
                        "link": entry.link,
                        "source": source_names.get(target_url, "Unknown"),
                        "date": translated_pub_date,
                        "datetime": pub_date
                    })
            else:
                # In case of emergency, pull back to direct scrape.
                pub_date = datetime.now()
                translated_pub_date = pub_date.strftime("%Y-%m-%d %H:%M")
                show_list.append({
                    "title": title,
                    "link": entry.link,
                    "source": source_names.get(target_url, "Unknown"),
                    "date": translated_pub_date,
                    "datetime": pub_date
                })
        return show_list  # Return the list of articles

    except Exception as e:
        print(f"Error scraping {target_url}: {e}")
    return show_list

def actualizar_html(articulos_frescos, html_file="index.html"):

    #Sección para hayar lista de artículos en index html
    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")
    except FileNotFoundError:
        print(f"Error: {html_file} no fue encontrado.")

    ul = soup.find("ul")
    if not ul:
        soup.body.append(ul)
        print("Error: No se ha encontrado un tag de tipo <ul> en el archivo.")
        return
    
    # Sección para evitar duplicados
    links_existentes = {li.find("a")["href"] for li in ul.find_all("li") if li.find("a")}

    for entry in articulos_frescos:
        if entry["link"] not in links_existentes:
            li = soup.new_tag("li")
            a = soup.new_tag("a", href=entry["link"], target="_blank")
            a.string = entry["title"]
            li.append(a)
            #Añade fuente y fecha
            li.append(f" - {entry['date']}")
            ul.insert(0,li)
            links_existentes.add(entry["link"])
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(str(soup))

    print(f"Updated {html_file} successfully!")

if __name__ == "__main__":
    if __name__ == "__main__":
        show_list = []
        for url in scrap_list:
            entries = scrape_article(url)  # Pass the URL
            if entries:  # Check if entries is not None
                show_list.extend(entries)
        actualizar_html(show_list)