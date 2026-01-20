from streamlit_interface.calculation_generator_v2 import (
    StreamlitCalculationGeneratorV2
)


def main() -> None:
    app = StreamlitCalculationGeneratorV2()
    app.streamlit_interface_method()


if __name__ == "__main__":
    main()
