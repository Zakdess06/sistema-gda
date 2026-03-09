# Configuración de instalación para Sistema GDA
from setuptools import setup, find_packages

setup(
    name="Sistema GDA",
    version="1.0.0",
    description="Sistema integral de gestión de almacén",
    author="Tu Nombre",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PySide6>=6.5",
        "openpyxl",
        "matplotlib>=3.5.0",
    ],
    entry_points={
        'console_scripts': [
            'sistema-gda=app.main:main',
        ],
        'gui_scripts': [
            'sistema-gda-gui=app.main:main',
        ],
    },
    package_data={
        'app': [
            'styles/*.qss',
            'resources/*',
        ],
    },
    python_requires='>=3.9',
)
