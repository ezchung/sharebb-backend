Phil & Ezra's Talking Points:

- Fix route for username link, button for editing user info ***DONE
- Clean up HTML (image sizing)
- Search function ***DONE
- Include upload in "Add Location" ***DONE
- Include route to delete location
- Add page to show location details (html, route) ***DONE
- Fix logout button ***DONE
- Show flashed error messages for login, signup, add location, edit ***DONE
- Added username of person who booked the property ***DONE
- Add card divs to others like in home ***DONE
- TODO: Establish messages

1. Booking
   Create table/model for booking ***DONE
   Connect booking with users & locations ***DONE
   Click image on homepage to go to location ID (show details) and be able to book location ***DONE

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

TODO:
WHAT WE DO NEXT
- Add messages (temporary)
   - through maybe websockets (socket.io)

- Add a map 
   - through maybe Google Maps API

- Make error messages clear on validate.
   - Do not know which field is creating error


Phil
- AWS
- Form Validation
- ORM / Database 
- What we planned on doing and what we already did

Ezra
- Maps API. How when we consider other libraries, our database needs to change
   - on what information we store
- Possibly combining two forms into one. AWS and database
