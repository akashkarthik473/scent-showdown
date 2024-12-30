# scent-showdown
#### Video Demo:  <URL HERE>
#### Description:

Scent Showdown is a web-based game that combines elements of fragrance appreciation with the thrill of a King of the Hill (KotH) competition. My inspiration came from a fascination with colognes and the desire to create something both unique and accessible. I decided to focus primarily on the design of fragrance bottles, rather than the scents themselves, which makes it possible for anyone to play—whether they are fragrance enthusiasts or complete newcomers.

Motivation and Initial Concept

My journey began when I delved  into the world of fragrances. I spent countless hours researching popular colognes and discussed them with my roommate. As a CS developer, I saw an opportunity to blend two of my interests: web development and fragrance. Initially, I wasn’t sure what form my project would take, but I knew I wanted to incorporate a “voting” or “competition” mechanic. Over time, this idea evolved into a King of the Hill framework, where fragrances battle for the top spot.

Data Collection and Preparation

One of the first challenges I faced was finding a reliable source of images for popular colognes. After exploring various websites, I decided to scrape Fragrantica because it offers a comprehensive library of fragrance information. I wrote a Python script to automate the image download process. Specifically, the script scrapes Fragrantica to grab images of the top 20 most popular fragrances at that time. The reason for this is that I was having issues with Selenium and BeautifulSoup so the only way I was able to get the images was by manually downloading the html and scraping it. In the future, I plan to expand this approach to feature up to 1,000 fragrances, which would give players a vast array of bottles to choose from.
Rather than storing the entire image URL for each fragrance, I noticed that Fragrantica uses a consistent URL format. By extracting just the numerical portion of the URL (the fragrance ID), I could significantly reduce the amount of data stored in my database. This design choice is pivotal because it helps keep the project scalable, making it easier to add new colognes without overwhelming database storage.

Database Design

For the database, I use a few tables that track different aspects of the game:
Fragrances Table: Stores the IDs and primary key
Votes: Records how many times each fragrance has won in the competition.
Wins: (Added on in the final stage of my website)

Front-End and User Interface

For the front-end, I envisioned a luxurious feel that would mirror the premium nature of high-end colognes. To do this, I selected a black-and-gold color palette and chose a font that conveyed that elegance. The styling is primarily done through CSS, ensuring that visual elements like buttons, text, and images align with the overall theme.
Initially, the website loaded two random fragrance images side-by-side. A user would click the one they preferred, and the page would then reload or use AJAX to pull in a new set of random images. This gave me a basic game loop, but at first, it lacked a definitive ending. The design was appealing, but I needed a core mechanic that would keep players engaged beyond simple voting.

Early Voting Prototype

My first working prototype was a basic “global vote” system. Every time a user selected a fragrance, a script using AJAX would increment a vote count in the database. Over time, I hoped to see a clear favorite emerge. Although this system worked, it felt more like a market research tool than an actual game. It provided insights into user preferences but didn’t maintain a sense of progression or competition.

The Shift to King of the Hill
After some user testing with friends, I realized that repeated appearances of the same cologne in the voting pool felt repetitive. One friend suggested removing the chosen fragrance from the immediate set, which sparked the idea to develop a King of the Hill mechanism. This new approach would track “wins” rather than votes and would also ensure that once a fragrance was selected (or defeated), it either advanced or was temporarily removed from the rotation.
I replaced the vote-accumulation logic with a more dynamic system:
Win Counter: Instead of simply recording a plus-one vote, the chosen fragrance’s “win” count increments.
Removal or Replacement: The defeated fragrance is temporarily removed from the pool, bringing in a new competitor for the next round.
The immediate impact was that the game felt more competitive and more like a tournament, with each selection bringing the user closer to a final champion.

Hall of Fame
To wrap up the competitive element, I designed a “Hall of Fame” page. This section showcases the fragrance that remained undefeated at the end of a session and displays a descending order of colognes by their accumulated wins. This leaderboard offers a quick snapshot of the “top bottles” among users, injecting some ongoing excitement into the experience.

Lessons Learned and Future Plans

Throughout the development process, I leaned heavily on AI assistance to help with JavaScript and AJAX, as I’m still improving my backend skills. ChatGPT provided valuable advice on structuring the code, optimizing database calls, and refining the user flow. Now that the core game loop is complete, I’m considering adding features like:
User Accounts: Allowing players to create profiles track their personal fragrance preferences and win records.
Extended Fragrance Library: Expanding from 20 to 1,000 fragrances to offer more variety.
Community Rankings: Implementing a system where users can see how their favorite fragrances stack up worldwide.
Additional Sorting Options: Providing filters or categories, such as “Designer,” “Niche,” or even “Celebrity” fragrances, to create smaller tournaments.
Conclusion

Scent Showdown represents the culmination of a passion for both web development and the world of fragrances. By focusing on bottle design and a King of the Hill format, the site welcomes players of all backgrounds. Whether you’re a seasoned fragrance connoisseur or simply a curious newcomer, Scent Showdown offers a fun and engaging way to discover and appreciate colognes from around the world. I hope you enjoy this project as much as I enjoyed creating it, and I look forward to expanding its features in the near future!



