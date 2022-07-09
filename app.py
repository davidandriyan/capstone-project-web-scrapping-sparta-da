from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import requests

# don't change this
matplotlib.use('Agg')
app = Flask(__name__)  # do not change this

# insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content, "html.parser")

# find your right key here
table = soup.find('table', attrs={
                  'class': 'table table-striped table-hover table-hover-solid-row table-simple history-data'})
row = table.find_all('tr')

row_length = len(row)

temp = []  # initiating a list

for i in range(0, row_length):

    # scrapping process
    row = table.find_all('tr')[i]

    date = row.find_all('td')[0].text  # get date
    date = date.strip()  # to remove excess white space

    day = row.find_all('td')[1].text  # get day
    day = day.strip()  # to remove excess white space

    ex_rates = row.find_all('td')[2].text  # get exchange rates
    ex_rates = ex_rates.strip()  # to remove excess white space

    temp.append((date, day, ex_rates))  # append the needed information

temp = temp[::-1]

# change into dataframe
df = pd.DataFrame(temp, columns=('date', 'day', 'ex_rates'))

# insert data wrangling here

# change date data types to datetime64
df['date'] = df['date'].astype('datetime64')
df['ex_rates'] = df['ex_rates'].str.replace(',', '')  # remove coma
df['ex_rates'] = df['ex_rates'].str.replace('IDR', '')  # remove IDR
# change ex_rate data types to float64
df['ex_rates'] = df['ex_rates'].astype('float64')
df = df.set_index('date')
# end of data wranggling


@app.route("/")
def index():

    # be careful with the " and '
    card_data = f'{df["ex_rates"].mean().round(2)}'

    # generate plot
    ax = df.plot(figsize=(20, 9))

    # Rendering plot
    # Do not change this
    figfile = BytesIO()
    plt.savefig(figfile, format='png', transparent=True)
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    plot_result = str(figdata_png)[2:-1]

    # render to html
    return render_template('index.html',
                           card_data=card_data,
                           plot_result=plot_result
                           )


if __name__ == "__main__":
    app.run(debug=True)
