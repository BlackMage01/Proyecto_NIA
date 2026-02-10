import feedparser
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from datetime import datetime
import os


# Feeds de interés: 
''' Specific RSS urls (these are the equivalent to an XML made link) '''

skynews_url = "https://fetchrss.com/feed/1vcX6N3ZM7Ax1vkbXg1qT7cJ.rss" #Sky news - Fetch RSS
AP_news_url = "https://fetchrss.com/feed/1vcX6N3ZM7Ax1vcX1O51y8g7.rss" #AP news - Fetch RSS 
efe_url = "https://fetchrss.com/feed/1vcX6N3ZM7Ax1vkZSa06Y78M.rss" #efe.com - Fetch RSS

scrap_list = [AP_news_url,skynews_url,efe_url]

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
            skynews_url: "Sky News",
            efe_url: "efe.com"
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

        for entry in feed.entries[:50]:
            print(f"Original pubDate:")
            title = entry.title
            if target_url == skynews_url:
                try:
                    title = GoogleTranslator(source='auto', target='es').translate(title)
                    print(f"Translated title: {title}")
                except Exception as e:
                    print(f"Translation failed for {title}: {e}")

            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6]) #tupla es convertida en datetime

                # Format the date in the desired format
                day_abbr = pub_date.strftime("%a")
                month_abbr = pub_date.strftime("%b")

                trans_day = day_names.get(day_abbr, day_abbr)
                trans_month = month_names.get(month_abbr, month_abbr)

                trans_pub_date = f"{trans_day}, {pub_date.day} {trans_month} {pub_date.year} {pub_date.strftime('%H:%M')}"

                show_list.append({
                    "title": title,
                    "link": entry.link,
                    "source": source_names.get(target_url, "Unknown"),
                    "date": trans_pub_date,
                    "datetime": pub_date
                })
            else:
                # Fallback to current date if pubDate is missing
                pub_date = datetime.now()
                trans_pub_date = f"{day_names.get(pub_date.strftime('%a'))}, {pub_date.day} {month_names.get(pub_date.strftime('%b'))} {pub_date.year} {pub_date.strftime('%H:%M')}"
                show_list.append({
                    "title": title,
                    "link": entry.link,
                    "source": source_names.get(target_url, "Unknown"),
                    "date": trans_pub_date,
                    "datetime": pub_date
                })
        return show_list

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
    
    # Sección para categorizar artículos
    articulos_frescos.sort(key=lambda x: x["datetime"], reverse=False)

    # Sección para evitar duplicados
    links_existentes = {li.find("a")["href"] for li in ul.find_all("li") if li.find("a")}

    for entry in articulos_frescos:
        if entry["link"] not in links_existentes:
            li = soup.new_tag("li")
            a = soup.new_tag("a", href=entry["link"], target="_blank")
            a.string = entry["title"]
            li.append(a)
            #Añade fuente y fecha
            li.append(f" - {entry['source']} | {entry['date']}")
            ul.insert(0,li)
            links_existentes.add(entry["link"])
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(str(soup))

    print(f"Updated {html_file} successfully!")

def generar_excel_mensual(articles):
    df = pd.DataFrame(articles)

    #Extraer mes y año en base a datetime
    df['Month'] = df['datetime'].dt.strftime('%Y-%m')

    #Agrupar en base a mes
    grouped = df.groupby('Month')

    #Crear un directorio con los documentos
    os.makedirs('excel_files', exist_ok=True)

    #Guarda cada mes de artículos como un excel separado
    for month, group in grouped:
        filename = f"excel_files/articulos_{month}.xlsx"
        group.to_excel(filename, index=False, engine='openpyxl')
        print(f"Saved {filename}")
        print("Todos los archivos Excel fueron guardados satisfactoriamente.")

if __name__ == "__main__":
    show_list = []
    for url in scrap_list:
        entries = scrape_article(url)  # Pass the URL
        if entries:  # Check if entries is not None
            show_list.extend(entries)

    #Sort por versión más reciente:
    show_list.sort(key=lambda x: x["datetime"],reverse=False)

    #Remove duplicates
    unique_articles = {}
    for article in show_list:
        title = article["title"]
    if title not in unique_articles:
        unique_articles[title] = article

    #Convert from dictionary values back to list
    unique_articles_list = list(unique_articles.values())

    #Sort the unique articles again by datetime, newest first
    unique_articles_list.sort(key=lambda x: x["datetime"], reverse=True)


    actualizar_html(show_list)

