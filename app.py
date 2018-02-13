from flask import Flask, render_template
from flask import *
import pandas as pd
import sqlite3

app = Flask(__name__)

@app.route('/')
def startpage():
	return render_template('startpage.html')

@app.route('/skincare')
def skincare():
	return render_template('skincare.html')

@app.route('/bathandbody')
def bathandbody():
	return render_template('bathandbody.html')

@app.route('/fragranceandgifts')
def fragranceandgifts():
	return render_template('fragranceandgifts.html')

@app.route('/bybrand')
def bybrand():
	return render_template('bybrand.html')

@app.route('/results', methods=['POST'])
def results():
	titletmp = "Results " + request.form.get('pagename')
	haircolor = request.form.get('haircolor')
	skintone = request.form.get('skintone')
	skintype = request.form.get('skintype')
	eyecolor = request.form.get('eyecolor')
	brand = request.form.get('brand')
	pagename = request.form.get('pagename')

	tmpsqlquery = 'SELECT brand_name, substr(product, 1, 40), p_category, ROUND(AVG(r_star),2) \
		AS avg_star, p_num_reviews, p_price FROM'

	if pagename=="Bath and Body":
		if (haircolor=='%') & (skintone=='%') & (eyecolor=='%'):
			tmpfilters = ' \
			( \
				SELECT * FROM sephora WHERE p_num_reviews>50 \
				AND (p_category="Bath & Body" OR p_category="Hair") \
			) \
			GROUP BY product ORDER BY avg_star DESC LIMIT 50'
		else:
			tmpfilters = ' \
			( \
				SELECT * FROM sephora WHERE p_num_reviews>50 \
				AND (p_category="Bath & Body" OR p_category="Hair") AND \
					( \
					((r_haircolor LIKE {}{}{}) AND\
					(r_skintone LIKE {}{}{})) OR\
					(r_eyecolor LIKE {}{}{}) \
					) \
			) \
			GROUP BY product ORDER BY avg_star DESC LIMIT 50'.format(
				"'",haircolor,"'","'",skintone,"'","'",eyecolor,"'"
				)
		sqlquery = tmpsqlquery + tmpfilters

	elif pagename=="Fragrance and Gifts":
		if (haircolor=='%') & (skintone=='%'):
			tmpfilters = ' \
			( \
				SELECT * FROM sephora WHERE p_num_reviews>50 \
				AND (p_category="Fragrance" OR p_category="Gifts" OR p_category="Men") \
			) \
			GROUP BY product ORDER BY avg_star DESC LIMIT 50'
		else:
			tmpfilters = ' \
			( \
				SELECT * FROM sephora WHERE p_num_reviews>50 \
				AND (p_category="Fragrance" OR p_category="Gifts" OR p_category="Men") AND \
					( \
					(r_haircolor LIKE {}{}{}) AND\
					(r_skintone LIKE {}{}{}) \
					) \
			) \
			GROUP BY product ORDER BY avg_star DESC LIMIT 50'.format(
				"'",haircolor,"'","'",skintone,"'"
				)
		sqlquery = tmpsqlquery + tmpfilters
		
	elif pagename=="Skincare":
		if (skintype=='%') & (skintone=='%'):
			tmpfilters = ' \
			( \
				SELECT * FROM sephora WHERE p_num_reviews>50 \
				AND (p_category="Skincare" OR p_category="Makeup" OR p_category="Tools & Brushes") \
			) \
			GROUP BY product ORDER BY avg_star DESC LIMIT 50'
		else:
			tmpfilters = ' \
			( \
				SELECT * FROM sephora WHERE p_num_reviews>50 \
				AND (p_category="Skincare" OR p_category="Makeup" OR p_category="Tools & Brushes") AND \
					( \
					(r_skintype LIKE {}{}{}) AND\
					(r_skintone LIKE {}{}{}) \
					) \
			) \
			GROUP BY product ORDER BY avg_star DESC LIMIT 50'.format(
				"'",skintype,"'","'",skintone,"'"
				)
		sqlquery = tmpsqlquery + tmpfilters

	elif pagename=="Brand":
		if (brand=='%'):
			tmpfilters = ' \
			( \
				SELECT * FROM sephora WHERE p_num_reviews>50 \
			) \
			GROUP BY product ORDER BY avg_star DESC LIMIT 50'
		else:
			tmpfilters = ' \
			( \
				SELECT * FROM sephora WHERE p_num_reviews>50 \
				AND \
					( \
					(brand_name LIKE {}{}{}) \
					) \
			) \
			GROUP BY product ORDER BY avg_star DESC LIMIT 50'.format(
				"'",brand,"'"
				)
		sqlquery = tmpsqlquery + tmpfilters

	print (sqlquery)
	con = sqlite3.connect("sephora.db")
	cur = con.cursor()
	cur.execute(sqlquery)
	rows = cur.fetchall()
	con.commit()
	con.close()
    
	return render_template('results.html', title=titletmp, rows=rows)


if __name__ == "__main__":
	app.run()
