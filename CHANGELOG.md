## 0.6.3 (Sep 6, 2021)

### Added
* Github actions for CI
* Added pybotx dependency to pyproject.toml (need for linter)

### Fixed
* Fix linter's warnings
___

## 0.6.2 (Aug 23, 2021)

### Fixed
* Fix saving data into `message.data`

### Changed
* Update `README.md`
---

## 0.6.1 (Aug 17, 2021)

### Changed
* refactoring `send_or_update_message` method to use metadata
---

## 0.6.0 (Aug 16, 2021)

### Changed
* **Breaking change:** change `display` method


### Removed
* **Breaking change:** remove  `merge_murkup` function from `service.py`
---


## 0.5.1 (Aug 16, 2021)

### Changed
* **Breaking change:** change `Checktable` and `Checklist` widgets implementation to class

---


## 0.5.0 (Aug 3, 2021)

### Changed
* **Breaking change:** change `Carousel` widget implementation to class

---

## 0.4.3 (Aug 2, 2021)

### Fix
* `MONTH_TO_DISPLAY_KEY` in `message.data` for `CalendarWidget`

---

## 0.4.2 (Aug 2, 2021)

### Changed
* **Breaking change:** change `Calendar` widget implementation to class

### Added
* Base class `Widget`

###Removed
* `botx` dependency from `pyproject.toml`
