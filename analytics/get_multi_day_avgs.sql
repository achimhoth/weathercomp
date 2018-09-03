DROP PROCEDURE IF EXISTS get_multi_day_avgs;

DELIMITER //
CREATE PROCEDURE get_multi_day_avgs(day_count int)
BEGIN

	drop table if exists temp_avgs;

	create temporary table if not exists temp_avgs as (select
		p.city,
		p.service,
		p.curr_date as _from,
		DATE_ADD(p.curr_date, INTERVAL day_count DAY) as _to,
		avg(abs(m.temp_max - p.temp_max)) as temp_max_delta,
		avg(abs(m.temp_min - p.temp_min)) as temp_min_delta,
		count(m.temp_max) as m_count
	from predictions as p
	join measurements as m on p.pred_date = m.date and p.city = m.city
	where pred_date <= DATE_ADD(p.curr_date, INTERVAL day_count DAY)
	group by p.curr_date, p.city, p.service
	order by p.curr_date, p.city, p.service, p.curr_date, p.pred_date);

	select
		t.city,
		t.service,
		round( avg(t.temp_max_delta) + avg(t.temp_min_delta), 2) as temp_delta,
		count(t.m_count) as sample_num
	from temp_avgs as t
	where t.m_count = day_count
	group by t.city, t.service
	order by t.city, temp_delta;

END //
DELIMITER ;

call get_multi_day_avgs( 1 );
