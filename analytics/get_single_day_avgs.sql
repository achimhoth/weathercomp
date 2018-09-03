DROP PROCEDURE IF EXISTS get_single_day_avgs;

DELIMITER //
CREATE PROCEDURE get_single_day_avgs(day_count int)
BEGIN

	drop table if exists temp_forecasts;

	create temporary table if not exists temp_forecasts as (select
		p.city,
		p.service,
		p.curr_date as _on,
		DATE_ADD(p.curr_date, INTERVAL day_count DAY) as _for,
		round(abs(m.temp_max - p.temp_max),2) as temp_max_delta,
		round(abs(m.temp_min - p.temp_min),2) as temp_min_delta,
		p.temp_max as temp_max_p,
		m.temp_max as temp_max_m
	from predictions as p
	join measurements as m on p.pred_date = m.date and p.city = m.city
	where pred_date > DATE_ADD(p.curr_date, INTERVAL day_count-1 DAY) and pred_date <= DATE_ADD(p.curr_date, INTERVAL day_count DAY)
	group by p.curr_date, p.city, p.service
	order by p.curr_date, p.city, p.service, p.curr_date, p.pred_date);

	select
		t.city,
		t.service,
		round( avg(t.temp_max_delta) + avg(t.temp_min_delta), 2) as temp_delta,
		count(t.temp_max_delta) as sample_num
	from temp_forecasts as t
	group by t.city, t.service
	order by t.city, temp_delta;

END //
DELIMITER ;

call get_single_day_avgs( 2 );
