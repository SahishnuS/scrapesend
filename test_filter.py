from internhunt.playwright.ats.base import JobListing
from internhunt.playwright.ats.filters import is_relevant_internship, INTERN_PATTERN, DOMAIN_PATTERN, EXCLUDE_PATTERN

listing = JobListing(
    title="Software Engineer Intern, Embedded Firmware",
    url="https://example.com",
    location="Singapore",
    description="Embrace the role of Hewlett Packard Enterprise as a Software Engineer Intern in Embedded Firmware. Collaborate with top technologists, design and validate cutting-edge networking products, and gain hands-on experience in software development. Ideal for students in Computer Engineering, Computer Science, or Electrical Engineering eager to grow in a dynamic, global environment."
)

print("is_relevant_internship:", is_relevant_internship(listing))
print("INTERN_PATTERN match:", INTERN_PATTERN.search(" ".join([listing.title, listing.location, listing.description])))
print("DOMAIN_PATTERN match:", DOMAIN_PATTERN.search(" ".join([listing.title, listing.location, listing.description])))
print("EXCLUDE_PATTERN match:", EXCLUDE_PATTERN.search(listing.title))
