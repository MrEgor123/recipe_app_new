import navigation from '../../configs/navigation'
import styles from './style.module.css'
import { useLocation } from 'react-router-dom'
import { LinkComponent } from '../index.js'

const NavMenu = ({ loggedIn }) => {
  const location = useLocation()

  return (
    <ul className={styles['nav-menu']}>
      {navigation.map(item => {
        if (!loggedIn && item.auth) return null

        return (
          <li className={styles['nav-menu__item']} key={item.href}>
            <LinkComponent
              title={item.title}
              href={item.href}
              exact
              className={styles['nav-menu__link']}
              activeClassName={styles['nav-menu__link_active']}
            />
          </li>
        )
      })}
    </ul>
  )
}

export default NavMenu