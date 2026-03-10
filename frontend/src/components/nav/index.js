import styles from './style.module.css'
import { useEffect, useState } from 'react'
import { AccountMenu, NavMenu, AccountMenuMobile } from '../index.js'
import cn from 'classnames'
import { useLocation } from 'react-router-dom'

const Nav = ({ loggedIn, onSignOut, orders }) => {
  const [menuToggled, setMenuToggled] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const cb = () => setMenuToggled(false)
    window.addEventListener('resize', cb)
    return () => window.removeEventListener('resize', cb)
  }, [])

  useEffect(() => {
    setMenuToggled(false)
  }, [location.pathname])

  return (
    <div className={styles.nav}>
      <div className={styles.nav__container}>
        <NavMenu loggedIn={loggedIn} />
        <AccountMenu onSignOut={onSignOut} orders={orders} />
      </div>

      <button
        type="button"
        className={styles.menuButton}
        onClick={() => setMenuToggled(!menuToggled)}
        aria-label="Меню"
      >
        <span className={styles.menuIcon} />
      </button>

      <div className={cn(styles['nav__container-mobile'], {
        [styles['nav__container-mobile_visible']]: menuToggled
      })}>
        <NavMenu loggedIn={loggedIn} />
        <AccountMenuMobile onSignOut={onSignOut} orders={orders} />
      </div>
    </div>
  )
}

export default Nav