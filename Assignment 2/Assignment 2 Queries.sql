-- Assignment 2 SQL Queries

-- 1. Retrieve the first name, last name, and email address of every customer in the database. 
-- Order the results alphabetically by last name.

SELECT c.first_name, c.last_name, c.email
FROM customer as c
ORDER BY c.last_name ASC


-- 2. List the name and unit price of all tracks that have a 
-- unit price greater than $0.99. Order by unit price descending.

SELECT t.name, t.unit_price
FROM track as t
WHERE t.unit_price > .99
ORDER BY t.unit_price DESC


-- 3. Find the total number of tracks in the database.

SELECT COUNT(*) as track_total
FROM track


/* 
4. List each customer's full name (first + last) alongside the total number of invoices they have. 
Only include customers who have placed more than 3 invoices. Order by invoice count descending.
*/
/*
SELECT CONCAT(c.first_name, ' ', c.last_name) as full_name, i.invoice_id
FROM customer as c
JOIN invoice as i ON c.customer_id = i.customer_id
ORDER BY full_name
*/

SELECT CONCAT(c.first_name, ' ', c.last_name) as full_name, COUNT(i.invoice_id) as invoice_count
FROM customer as c
JOIN invoice as i ON c.customer_id = i.customer_id
GROUP BY full_name
HAVING COUNT(i.invoice_id) > 3
ORDER BY invoice_count DESC

/* 
5. Find the top 5 most purchased tracks (by quantity sold across all invoices). 
Display the track name and total quantity sold.
*/

SELECT t.name, SUM(il.quantity) as total_quantity
FROM track as t
JOIN invoice_line as il ON t.track_id = il.track_id
GROUP BY t.track_id
ORDER BY total_quantity DESC
LIMIT 5;

/*
6. List all albums along with the name of the artist who made 
them and the total number of tracks on each album. Order by track count descending.
*/

SELECT al.title, art.name, COUNT(t.track_id) as track_total
FROM album as al
JOIN artist as art ON al.artist_id = art.artist_id
JOIN track as t ON al.album_id = t.album_id 
GROUP BY al.title, art.name
ORDER BY track_total DESC

/*
7. Find all customers who are located in the same country as their 
assigned support representative (sales agent). 
Return the customer's full name, the rep's full name, and the country.
*/

SELECT CONCAT(c.first_name, ' ', c.last_name) as customer_name, 
	CONCAT(e.first_name, ' ', e.last_name) as employee_name,
	c.country
FROM customer as c
JOIN employee as e ON c.support_rep_id = e.employee_id
WHERE c.country = e.country


/*
8. Calculate the total revenue generated per genre. 
Display the genre name and total revenue, ordered by revenue descending.
*/

SELECT g.name, SUM(il.quantity * il.unit_price) as total_revenue
FROM genre as g 
JOIN track as t ON g.genre_id = t.genre_id
JOIN invoice_line as il ON t.track_id = il.track_id
GROUP BY g.name
ORDER BY total_revenue DESC


/*
9. Find the month-over-month revenue for the year 2021. 
Display the month number, month name, and total revenue for each month. 
(Hint: use TO_CHAR or DATE_PART.)
*/


SELECT DATE_PART('month', i.invoice_date) AS month_number,
	TO_CHAR(i.invoice_date, 'Month') AS month_name,
	SUM(i.total)
FROM invoice as i
WHERE DATE_PART('year', i.invoice_Date) = 2021
GROUP BY month_number, month_name
ORDER BY month_number


/*
10. Identify customers who have never purchased a 
track from the 'Rock' genre. Return their full name and email. 
(Hint: this is the same LEFT JOIN + IS NULL 
anti-join shape from this week's demo — 
a plain INNER JOIN can't express "this never happened.")
*/

SELECT CONCAT(c.first_name, ' ', c.last_name) as customer_name, 
	c.email
FROM customer as c
LEFT JOIN invoice as i ON c.customer_id = i.customer_id
LEFT JOIN invoice_line as il ON i.invoice_id = il.invoice_id
LEFT JOIN track as t ON il.track_id = t.track_id
LEFT JOIN genre as g ON g.genre_id = t.genre_id
WHERE g.name <> 'Rock'
GROUP BY customer_name, c.email

/*
11. For each country, find the single highest-spending customer. 
Display the country, the customer's full name, and their total spend.

(A clean way to do this is a window function — RANK() 
or ROW_NUMBER() with PARTITION BY — though a subquery can 
also get you there. If you go the window-function route: 
PostgreSQL's window functions tutorial and the window function reference.)
*/


WITH customer_totals as (
	SELECT CONCAT(c.first_name, ' ', c.last_name) as customer_name, 
		SUM(il.quantity * il.unit_price) as total,
		c.country,
		ROW_NUMBER() OVER (
			PARTITION BY c.country
			ORDER BY SUM(il.quantity * il.unit_price) DESC
		) as row_num
	FROM customer as c
	JOIN invoice as i ON c.customer_id = i.customer_id
	JOIN invoice_line as il ON i.invoice_id = il.invoice_Id
	GROUP BY customer_name, c.country
)

SELECT c.customer_name, c.total, c.country 
FROM customer_totals as c
WHERE c.row_num = 1


/* 
12. Find all tracks that have never been purchased. Display the track name, album title, and artist name.
*/ 

SELECT t.name as track, a.title as album, art.name as artist
FROM track as t
LEFT JOIN invoice_line as il ON t.track_id = il.track_id
JOIN album as a ON t.album_id = a.album_id
JOIN artist as art ON a.artist_id = art.artist_id
WHERE il.quantity IS NULL


