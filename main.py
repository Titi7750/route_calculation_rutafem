""" Python version : 3.13.9 """

from streamlit_interface.calculation_generator_file import StreamlitCalculationGenerator

# -----

def main() -> None:
    """ Main function to run the route calculation """

    interface = StreamlitCalculationGenerator()
    interface.streamlit_interface_method()

# -----

if __name__ == "__main__":
    main()
