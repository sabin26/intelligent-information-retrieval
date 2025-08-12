import sys
import os
import asyncio

# Ensure the project root is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import crawl
from indexer import build_index
from search import run_search_interface

def print_usage():
    """Prints the usage instructions for the main script."""
    print("Usage: python main.py [command]")
    print("\nCommands:")
    print("  crawl   - Start the web crawler to fetch publication data.")
    print("  index   - Build the search index from the crawled data.")
    print("  search  - Start the interactive search interface.")
    print("\nExample workflow:")
    print("  1. python main.py crawl")
    print("  2. python main.py index")
    print("  3. python main.py search")

def main():
    """Main function to orchestrate the search engine components."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == 'crawl':
        # Use asyncio.run() to execute the async crawl function
        asyncio.run(crawl())
    elif command == 'index':
        build_index()
    elif command == 'search':
        run_search_interface()
    else:
        print(f"Error: Unknown command '{command}'")
        print_usage()

if __name__ == '__main__':
    main()