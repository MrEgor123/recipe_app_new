import { useState } from 'react'

import styles from './style.module.css'
import Container from '../container'
import LogoIcon from '../../images/recepto-icon.png'

const Footer = () => {
  const [isSupportOpen, setIsSupportOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  })
  const [isSending, setIsSending] = useState(false)
  const [statusMessage, setStatusMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const closeSupportModal = () => {
    setIsSupportOpen(false)
    setStatusMessage('')
    setErrorMessage('')
  }

  const handleInputChange = (event) => {
    const { name, value } = event.target

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSupportSubmit = (event) => {
    event.preventDefault()

    setIsSending(true)
    setStatusMessage('')
    setErrorMessage('')

    fetch('/api/support/requests/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: formData.name.trim(),
        email: formData.email.trim(),
        message: formData.message.trim(),
      }),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Не удалось отправить обращение')
        }

        return res.json()
      })
      .then(() => {
        setStatusMessage('Обращение отправлено. Администратор обработает его в панели управления.')
        setFormData({
          name: '',
          email: '',
          message: '',
        })
      })
      .catch(() => {
        setErrorMessage('Не удалось отправить обращение. Попробуйте позже или перейдите в Telegram.')
      })
      .finally(() => {
        setIsSending(false)
      })
  }

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
            <button
              type="button"
              className={`${styles.link} ${styles.supportLink}`}
              onClick={() => setIsSupportOpen(true)}
            >
              поддержка
            </button>
          </nav>

          <div className={styles.meta}>© {new Date().getFullYear()}</div>
        </div>
      </Container>

      {isSupportOpen && (
        <div className={styles.modalOverlay} onClick={closeSupportModal}>
          <div className={styles.modal} onClick={(event) => event.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div>
                <h2 className={styles.modalTitle}>Поддержка</h2>
                <p className={styles.modalText}>
                  Можно перейти в Telegram или оставить обращение прямо на сайте.
                </p>
              </div>

              <button
                type="button"
                className={styles.closeButton}
                onClick={closeSupportModal}
                aria-label="Закрыть"
              >
                ×
              </button>
            </div>

            <a
              className={styles.telegramButton}
              href="https://t.me/MrEgorAP"
              target="_blank"
              rel="noreferrer"
            >
              перейти в Telegram
            </a>

            <form className={styles.supportForm} onSubmit={handleSupportSubmit}>
              <label className={styles.field}>
                <span>Имя</span>
                <input
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  maxLength={150}
                  placeholder="Как к вам обращаться"
                />
              </label>

              <label className={styles.field}>
                <span>Email для обратной связи</span>
                <input
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  maxLength={255}
                  placeholder="example@mail.ru"
                />
              </label>

              <label className={styles.field}>
                <span>Вопрос</span>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  required
                  minLength={5}
                  maxLength={3000}
                  placeholder="Опишите проблему или вопрос"
                />
              </label>

              {statusMessage && (
                <div className={styles.successMessage}>{statusMessage}</div>
              )}

              {errorMessage && (
                <div className={styles.errorMessage}>{errorMessage}</div>
              )}

              <button
                type="submit"
                className={styles.submitButton}
                disabled={isSending}
              >
                {isSending ? 'отправка...' : 'отправить обращение'}
              </button>
            </form>
          </div>
        </div>
      )}
    </footer>
  )
}

export default Footer