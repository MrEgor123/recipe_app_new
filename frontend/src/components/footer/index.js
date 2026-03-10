import styles from './style.module.css'
import Container from '../container'

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <Container>
        <div className={styles.footerContent}>
          <div className={styles.brand}>
            <div className={styles.brandTitle}>Recipe App</div>
            <div className={styles.brandSubtitle}>минималистичная книга рецептов</div>
          </div>

          <nav className={styles.links} aria-label="Навигация в подвале">
            <a className={styles.link} href="/">рецепты</a>
            <a className={styles.link} href="/favorites">избранное</a>
            <a className={styles.link} href="/shopping-cart">покупки</a>
            <a className={styles.link} href="/subscriptions">подписки</a>
          </nav>

          <div className={styles.meta}>© {new Date().getFullYear()}</div>
        </div>
      </Container>
    </footer>
  )
}

export default Footer