TODO:

- Fix route for username link, button for editing user info ***DONE
- Clean up HTML (image sizing)
- Search function ***DONE
- Include upload in "Add Location"  ***DONE
- Include route to delete user
- Add page to show location details (html, route) ***DONE
- show flashed error messages

1. Booking
   Create table/model for booking ***DONE
   Connect booking with users & locations ***DONE
   Click image on homepage to go to location ID (show details) and be able to book location

2. Get the url from AWS ***DONE
   and place image url into database

SQL Strings
`SELECT locations.address FROM bookings
   JOIN users ON users.id = bookings.user_id
   JOIN locations ON locations.id = bookings.location_id
   WHERE users.username LIKE 'phil';`

   - Returns address of locations where user whose username is phil has booked
Translation to SQLAlchemy
-

SELECT address FROM locations
   JOIN users ON users.id = locations.owner_id
   WHERE users.username = 'phil';

   - Getting the address where the owner of the location is phil.
Translation to SQLAlchemy
-