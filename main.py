''' Python version : 3.13.9 '''

from src.retrieve_data_file import RetrieverData

def main() -> None:

    retriever = RetrieverData()
    retriever.retrieve_data_fuel_method()

if __name__ == "__main__":
    main()
