
import asyncio
from leakradar.api import LeakRadarClient

async def main():
    # Replace with your actual Bearer token
    token = "YOUR_BEARER_TOKEN"

    async with LeakRadarClient(token=token) as client:
        # Fetch the authenticated user's profile
        profile = await client.get_profile()
        print("Profile:", profile)

        # Perform an advanced search with a username filter
        advanced_search_results = await client.search_advanced(username="john.doe@example.com")
        print("Advanced Search Results:", advanced_search_results)

        # Unlock all leaks matching advanced search filters
        unlocked_leaks = await client.unlock_all_advanced({"username": "john.doe@example.com"})
        print("Unlocked Leaks:", unlocked_leaks)

        # Export advanced search results as CSV
        csv_data = await client.export_advanced(username="john.doe@example.com")
        with open("advanced_search_results.csv", "wb") as f:
            f.write(csv_data)
        print("Exported advanced search results to 'advanced_search_results.csv'.")

        # Fetch domain report
        domain_report = await client.get_domain_report(domain="tesla.com")
        print("Domain Report:", domain_report)

        # Get domain customers
        domain_customers = await client.get_domain_customers(domain="tesla.com", page=1, page_size=10)
        print("Domain Customers:", domain_customers)

        # Get domain employees
        domain_employees = await client.get_domain_employees(domain="tesla.com", page=1, page_size=10)
        print("Domain Employees:", domain_employees)

        # Unlock specific leaks by ID
        leaks_to_unlock = [12345, 67890]  # Replace with actual leak IDs
        unlocked_specific_leaks = await client.unlock_specific_leaks(leaks_to_unlock)
        print("Unlocked Specific Leaks:", unlocked_specific_leaks)

        # Search for leaks associated with an email
        email_search_results = await client.search_email(email="john.doe@example.com", show_only_unlocked=True)
        print("Email Search Results:", email_search_results)

        # Export unlocked email leaks as CSV
        email_csv_data = await client.export_email_leaks(email="john.doe@example.com")
        with open("email_leaks.csv", "wb") as f:
            f.write(email_csv_data)
        print("Exported email leaks to 'email_leaks.csv'.")

        # Unlock all email leaks
        unlocked_email_leaks = await client.unlock_email_leaks(email="john.doe@example.com")
        print("Unlocked Email Leaks:", unlocked_email_leaks)

if __name__ == "__main__":
    asyncio.run(main())
