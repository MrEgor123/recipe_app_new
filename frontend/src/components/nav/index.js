import styles from './style.module.css'
import { useEffect, useState } from 'react'
import { AccountMenu, NavMenu, AccountMenuMobile, LinkComponent } from '../index.js'
import Icons from '../icons'
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

  const ordersCount = Number(orders) || 0

  return (
    <div className={styles.nav}>
      <div className={styles.nav__container}>
        <NavMenu loggedIn={loggedIn} />
        <AccountMenu onSignOut={onSignOut} orders={orders} />
      </div>

      <LinkComponent
        href="/cart"
        className={styles.mobileOrders}
        title={
          <>
            <Icons.Cart />

            {ordersCount > 0 && (
              <span className={styles.mobileOrdersCounter}>
                {ordersCount}
              </span>
            )}
          </>
        }
      />

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