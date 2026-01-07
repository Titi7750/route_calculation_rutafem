import streamlit as st
from streamlit_interface.calculation_generator_file import StreamlitCalculationGenerator

def main():
    app = StreamlitCalculationGenerator()
    app.streamlit_interface_method()

if __name__ == "__main__":
    main()
