import styles from './style.module.css'
import { Nav, LinkComponent } from '../index.js'
import Container from '../container'

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
                <div className={styles.brandTitle}>Recipe App</div>
                <div className={styles.brandSubtitle}>минималистичная книга рецептов</div>
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