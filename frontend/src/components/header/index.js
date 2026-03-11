import styles from './style.module.css'
import { Nav, LinkComponent } from '../index.js'
import Container from '../container'
import LogoIcon from '../../images/recepto-icon.png'

const Header = ({ loggedIn, onSignOut, orders }) => {
  return (
    <header className={styles.header}>
      <Container>
        <div className={styles.headerContent}>
          <LinkComponent
            className={styles.headerLink}
            href="/"
            title={
              <div className={styles.brand}>
                <img
                  src={LogoIcon}
                  alt="Recepto"
                  className={styles.brandIcon}
                />
                <span className={styles.brandTitle}>Recepto</span>
              </div>
            }
          />
          <Nav loggedIn={loggedIn} onSignOut={onSignOut} orders={orders} />
        </div>
      </Container>
    </header>
  )
}

export default Header