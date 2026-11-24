
from app import create_app


app = create_app()


if __name__ == "__main__":

    print("=" * 50)
    print("KAVACH ZERO 2.0")
    print("Continuous Zero-Trust Policy Assurance")
    print("=" * 50)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
