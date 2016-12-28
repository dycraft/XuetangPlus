import xlrd
import json

data = xlrd.open_workbook('2016_2017_2.xls')

jsonData = []

for index, table in enumerate(data.sheets()):
	print(table)
	print(index)
	for row in range(table.nrows):
		if(row < 2):
			continue
		val = table.row_values(row)
		if index == 0:
			jsonData.append({
				'school': val[0],
				'course_id': val[1],
				'course_seq': val[2],
				'course_name': val[3],
				'score': val[4],
				'teacher': val[5],
				'time': val[7],
				'week': val[8],
				'feature': val[9],
				'intro': val[10],
				'second': val[11],
				'year': val[12],
				})
		elif index == 9:
			jsonData.append({
				'school': val[0],
				'course_id': val[1],
				'course_seq': val[2],
				'course_name': val[3],
				'score': val[4],
				'teacher': val[5],
				'time': val[7],
				'week': val[8],
				'feature': '',
				'intro': val[9],
				'second': '',
				'year': '',
				})
		elif index == 8 or index == 7:
			jsonData.append({
				'school': val[0],
				'course_id': val[1],
				'course_seq': val[2],
				'course_name': val[3],
				'score': val[4],
				'teacher': val[5],
				'time': val[7],
				'week': val[8],
				'feature': val[9],
				'intro': val[10],
				'second': val[12],
				'year': '',
				})
		else:
			jsonData.append({
				'school': val[0],
				'course_id': val[1],
				'course_seq': val[2],
				'course_name': val[3],
				'score': val[4],
				'teacher': val[5],
				'time': val[7],
				'week': val[8],
				'feature': val[9],
				'intro': val[10],
				'second': val[11],
				'year': '',
				})


json.dump(jsonData,open('course.json','w'),indent = 4)