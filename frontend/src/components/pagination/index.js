import styles from './styles.module.css'
import cn from 'classnames'
import { useState, useEffect } from 'react'

const Pagination = ({ count = 0, limit = 6, initialActive = 1, onPageChange, page }) => {
  const [active, setActive] = useState(initialActive)

  const onButtonClick = nextActive => {
    setActive(nextActive)
    onPageChange(nextActive)
  }

  useEffect(_ => {
    if (page === active) return
    setActive(page)
  }, [page])

  const pagesCount = Math.ceil(count / limit)
  if (count === 0 || pagesCount <= 1) return null

  return (
    <div className={styles.pagination}>
      <div
        className={cn(styles.arrow, styles.arrowLeft, {
          [styles.arrowDisabled]: active === 1
        })}
        onClick={_ => {
          if (active === 1) return
          onButtonClick(active - 1)
        }}
        aria-label="Предыдущая страница"
        role="button"
        tabIndex={0}
      >
        <span className={styles.arrowIcon}>‹</span>
      </div>

      {(new Array(pagesCount)).fill().map((_, idx) => (
        <div
          className={cn(styles.paginationItem, {
            [styles.paginationItemActive]: idx + 1 === active
          })}
          onClick={_ => onButtonClick(idx + 1)}
          key={idx}
          aria-label={`Страница ${idx + 1}`}
          role="button"
          tabIndex={0}
        >
          {idx + 1}
        </div>
      ))}

      <div
        className={cn(styles.arrow, styles.arrowRight, {
          [styles.arrowDisabled]: active === pagesCount
        })}
        onClick={_ => {
          if (active === pagesCount) return
          onButtonClick(active + 1)
        }}
        aria-label="Следующая страница"
        role="button"
        tabIndex={0}
      >
        <span className={styles.arrowIcon}>›</span>
      </div>
    </div>
  )
}

export default Pagination