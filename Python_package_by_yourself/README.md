# 自己写 Python 库

## 创建前目录结构

```
│  LICENSE.txt
│  README.md
│  setup.py
│
└─number_theory
    │  property.py
    │  __init__.py
    │
    └─calculate
        │  arithmetic.py
        │  Euclidean_norm.py
        │  __init__.py
        │
        └─advanced
                Bezout_lemma.py
                __init__.py
```

## 创建过程

`python3 setup.py sdist bdist_wheel`

## 创建后目录结构

```
│  LICENSE.txt
│  README.md
│  setup.py
│
├─build
│  ├─bdist.win-amd64
│  └─lib
│      └─number_theory
│          │  property.py
│          │  __init__.py
│          │
│          └─calculate
│              │  arithmetic.py
│              │  Euclidean_norm.py
│              │  __init__.py
│              │
│              └─advanced
│                      Bezout_lemma.py
│                      __init__.py
│
├─dist
│      number theory-1.0.tar.gz
│      number_theory-1.0-py3-none-any.whl
│
├─number_theory
│  │  property.py
│  │  __init__.py
│  │
│  └─calculate
│      │  arithmetic.py
│      │  Euclidean_norm.py
│      │  __init__.py
│      │
│      └─advanced
│              Bezout_lemma.py
│              __init__.py
│
└─number_theory.egg-info
        dependency_links.txt
        PKG-INFO
        SOURCES.txt
        top_level.txt
```

## 参考

https://packaging.python.org/tutorials/packaging-projects/

