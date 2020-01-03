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

[https://zh.wikipedia.org/wiki/%E6%89%A9%E5%B1%95%E6%AC%A7%E5%87%A0%E9%87%8C%E5%BE%97%E7%AE%97%E6%B3%95](https://zh.wikipedia.org/wiki/扩展欧几里得算法)

