import styles from './style.module.css'
import Container from '../container'
import LogoIcon from '../../images/recepto-icon.png'

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <Container>
        <div className={styles.footerContent}>
          <div className={styles.brand}>
            <img
              src={LogoIcon}
              alt="Recepto"
              className={styles.brandIcon}
            />
            <div className={styles.brandTitle}>Recepto</div>
          </div>

          <nav className={styles.links} aria-label="Навигация в подвале">
            <a className={styles.link} href="/">рецепты</a>
            <a className={styles.link} href="/favorites">избранное</a>
            <a className={styles.link} href="/cart">покупки</a>
            <a className={styles.link} href="/subscriptions">подписки</a>
          </nav>

          <div className={styles.meta}>© {new Date().getFullYear()}</div>
        </div>
      </Container>
    </footer>
  )
}

export default Footer