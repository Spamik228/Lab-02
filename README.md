#  Inverted Index Engine (Lab-02)
## 📊 (M1) Результати побудови інвертованого індексу 

| Метрика                          |  Значення     |
|:---------------------------------|:--------------|
| **Проіндексовано документів**    | `1 000`       |
| **Унікальних термів (словник)**  | `11 581`      |
| **Розмір індексу (без позицій)** | `6.69 МБ`     |
| **Розмір індексу (з позиціями)** | `14.27 МБ`    |
| **Оверхед пам'яті (позиції)**    | **`+113.2%`** |
### Приклад структури постінгів (`Posting`)

```python
# Терм для прикладу: "a"

# 1. Без позицій
Posting(doc_id=0, tf=2, positions=())

# 2. З позиціями (для фразового пошуку)
Posting(doc_id=0, tf=2, positions=(0, 113))
```

## M2. Порівняння алгоритмів оцінки логічних запитів (`--engine merge` vs `--engine set`)

### 📊 Benchmark Results
```python
Найчастіші терми  : ['of', 'the'] (документів: 980, 978)
Найрідкісніші терми: ['cpv', 'arg'] (документів: 1, 1)
```
| Запит | Engine: MERGE (сек) | Engine: SET (сек) |
| :--- | :---: | :---: |
| **Common AND** | `0.621795 s` | `0.602083 s` |
| **Common OR** | `0.622369 s` | `0.597982 s` |
| **Common NOT** | `0.605158 s` | `0.581455 s` |
| **Rare AND** | `0.001775 s` | `0.002099 s` |
| **Rare OR** | `0.001813 s` | `0.002118 s` |
| **Rare NOT** | `0.079992 s` | `0.029856 s` |

---

## M3. Persistence Study

###  Формати збереження індексу (Save / Load Benchmark)
WARNING / SECURITY NOTE:
Never use `pickle.load()` on untrusted or untrusted-source files! 
Pickle allows execution of arbitrary Python code during deserialization(via __reduce__ exploit vectors). 
An attacker could construct a malicious file that executes shell commands upon loading.
Індекс підтримує збереження та відновлення у двох форматах (`pickle` та `json`). Заміри проводилися на повному корпусі файлів:

| Format | File Size (MB) | Save Time (s) | Load Time (s) |
| :--- | :---: | :---: | :---: |
| **pickle** | `1.39 MB` | `0.1374 s` | `0.1417 s` |
| **json** | `3.44 MB` | `0.3555 s` | `0.1414 s` |

---

##  M4. Memory Study — Структури постингу в пам'яті

### 📊 Three-Row Memory Table

| Postings representation | Peak memory (build) | Index file size | Load time |
| :--- | :---: | :---: | :---: |
| **`list[Posting]` `@dataclass`** | `13.90 MB` | `2.09 MB` | `0.0715 s` |
| **`list[Posting]` `slots=True`** | `10.93 MB` | `2.31 MB` | `0.0670 s` |
| **`array('I')` pairs** | `6.77 MB` | `2.65 MB` | `0.0365 s` |

---

### Розподіл пам'яті (Where the Bytes Went)

* **`list[Posting]` with plain `@dataclass`**: Кожен об'єкт у Python за замовчуванням створює динамічний словник атрибутів `__dict__` (112–152 байти) та CPython-заголовок `PyObject` (16–24 байти). У масштабі мільйонів постингів це створює величезні накладні витрати пам'яті.
* **`list[Posting]` with `slots=True`**: Використання `__slots__` фіксує атрибути класу у C-структурі й повністю видаляє `__dict__`. Це економить ~112 байт на кожен постинг, знижуючи пікове споживання RAM при побудові на **~35%** та зменшуючи розмір pickle-файлу.
* **`array('I')` pairs — no objects**: Повністю усуває концепцію окремого Python-об'єкта для кожного постингу. Постинги зберігаються у низькорівневих C-масивах 32-бітних цілих чисел (лише 4 байти на значення замість 28 байт для Python `int` + накладні витрати об'єкта). Це зменшує пікову пам'ять на **~75%** і забезпечує найшвидшу десеріалізацію через зчитування суцільного блоку пам'яті.