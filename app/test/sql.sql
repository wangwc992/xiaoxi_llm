# 174951	32	1373	Sydney Medical School Campuses and Teaching Hospitals	1370	艺术与社会科学学院	GNEDUSTD1EDL	教育研究生文凭（教育领导力）	Graduate Diploma in Educational Studies (Educational Leadership)		预科	Graduate Diploma	硕士预备	1年	2/年,1/年,		2024年2月19日，2024年7月29日				录取候选人需要：悉尼大学教育学士或同等学历，并完成研究生学习，或在学院认为适合学习项目的领域具有相当于一年全职的专业经验；或	https://www.sydney.edu.au/courses/courses/pc/graduate-diploma-in-educational-studies-educational-leadership.html		37125每年													雅思：总分6.5分，每级最低6.0分	6.5	托福-IBT成绩：总分最低85分，其中阅读、听力和口语最低17分，写作最低19分	85					0		0	0	1	3999		王文城	2023-11-07 15:35:25	2024-07-24 18:55:28	0			0					2024-02,2024-07	3678		024659C	0


SELECT t1.id, t1.chinese_name,t1.degree_type,t4.english_name,t1.length_of_schoolings,t1.length_of_full,t1.opening_month FROM zn_school_department_project t1
INNER JOIN zn_school_department_project_category t2 ON t2.zsdp_id = t1.id
INNER JOIN zn_school_major_category t3 ON t3.id = t2.category_id
INNER JOIN zn_school_info t4 ON t4.id = t1.school_id
INNER JOIN zn_school_rank t5 ON t5.school_id = t4.id

WHERE t4.country_name = '澳大利亚'
AND t5.world_rank_qs <= 50
AND t1.degree_type = '博士'
AND t4.english_name = 'UNSW Sydney'
AND (FIND_IN_SET('3/年', length_of_schoolings) OR length_of_full = '3.5年')
AND opening_month LIKE '%-2,%'