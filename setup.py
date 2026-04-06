from setuptools import setup, find_packages

setup(
    name="hzm-algebra",
    version="1.0.0",
    author="M. Dzhanbulatov",
    description="Hierarchical Zero Algebra (HZM) for Python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[],  # основные зависимости (если есть)
    extras_require={
        "ml": ["torch>=1.9.0"],          # зависимости для машинного обучения
        "full": ["torch>=1.9.0", "matplotlib"],  # полный набор
    },
    classifiers=[...],
)
