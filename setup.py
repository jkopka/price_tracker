from setuptools import setup

setup(
    name="pricetracker",
    packages=["pricetracker"],
    include_package_data=True,
    install_requires=["flask", "bs4", "tqdm", "requests", "matplotlib"],
)
