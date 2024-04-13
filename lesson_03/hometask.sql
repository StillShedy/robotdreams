/*
 Завдання на SQL до лекції 03.
 */


/*
1.
Вивести кількість фільмів в кожній категорії.
Результат відсортувати за спаданням.
*/
-- SQL code goes here...

select 
cat.category_id, 
count(cat.film_id) 
from public.film_category cat
group by cat.category_id
order by count(cat.film_id) desc
/*
2.
Вивести 10 акторів, чиї фільми брали на прокат найбільше.
Результат відсортувати за спаданням.
*/
-- SQL code goes here...

select 
a.first_name, 
a.last_name from public.actor a
left join public.film_actor fa on fa.actor_id = a.actor_id
left join public.film f on f.film_id = fa.film_id
group by a.first_name, a.last_name
order by avg(f.rental_rate) desc
limit 10

/*
3.
Вивести категорія фільмів, на яку було витрачено найбільше грошей
в прокаті
*/
-- SQL code goes here...

select c.name, sum(p.amount) from public.film_category fc
inner join public.category c on fc.category_id = c.category_id
inner join public.inventory i on fc.film_id = i.film_id
inner join public.rental r on i.inventory_id = r.inventory_id
inner join public.payment p on p.rental_id = r.rental_id
group by c.name
order by sum(p.amount) DESC
limit 1

/*
4.
Вивести назви фільмів, яких не має в inventory.
Запит має бути без оператора IN
*/
-- SQL code goes here...

select f.title from public.film f
left join public.inventory i on i.film_id = f.film_id
where i.film_id is null

/*
5.
Вивести топ 3 актори, які найбільше зʼявлялись в категорії фільмів “Children”.
*/
-- SQL code goes here...

select 
a.first_name, a.last_name, count(a.actor_id)
from public.actor a
left join public.film_actor fa on fa.actor_id = a.actor_id
left join public.film f on f.film_id = fa.film_id
left join public.film_category fc on fc.film_id = f.film_id
inner join public.category c on c.category_id = fc.category_id and c.name = 'Children'
group by a.first_name, a.last_name
order by count(a.actor_id) desc
limit 3