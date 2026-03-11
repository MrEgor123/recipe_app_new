import { Container, Main, Button } from "../../components";
import MetaTags from "react-meta-tags";
import styles from "./styles.module.css";
import LogoIcon from "../../images/recepto-icon.png";

const NotFound = () => {
  return (
    <Main>
      <Container>
        <MetaTags>
          <title>Страница не найдена — Recepto</title>
          <meta
            name="description"
            content="Страница не найдена в приложении Recepto"
          />
          <meta property="og:title" content="Страница не найдена — Recepto" />
        </MetaTags>

        <section className={styles.notFound}>
          <div className={styles.card}>
            <img src={LogoIcon} alt="Recepto" className={styles.logo} />

            <div className={styles.code}>404</div>

            <h1 className={styles.title}>Страница не найдена</h1>

            <p className={styles.text}>
              Похоже, такой страницы не существует или она была перемещена
            </p>

            <Button
              href="/"
              modifier="style_dark"
              className={styles.button}
            >
              На главную
            </Button>
          </div>
        </section>
      </Container>
    </Main>
  );
};

export default NotFound;