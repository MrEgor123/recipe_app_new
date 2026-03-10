import {
  Container,
  Input,
  Main,
  Form,
  Button,
  FormTitle,
} from "../../components";
import styles from "./styles.module.css";
import { useFormWithValidation } from "../../utils";
import { AuthContext } from "../../contexts";
import { Redirect } from "react-router-dom";
import { useContext } from "react";
import MetaTags from "react-meta-tags";

const SignIn = ({ onSignIn, submitError, setSubmitError }) => {
  const { values, handleChange, errors } = useFormWithValidation();
  const authContext = useContext(AuthContext);

  const onChange = (e) => {
    setSubmitError({ submitError: "" });
    handleChange(e);
  };

  return (
    <Main>
      {authContext && <Redirect to="/recipes" />}

      <Container className={styles.page}>
        <MetaTags>
          <title>Войти на сайт</title>
          <meta
            name="description"
            content="Recipe App - Войти на сайт"
          />
          <meta property="og:title" content="Войти на сайт" />
        </MetaTags>

        <div className={styles.authShell}>
          <Form
            className={styles.form}
            onSubmit={(e) => {
              e.preventDefault();
              onSignIn(values);
            }}
          >
            <FormTitle className={styles.title}>Войти</FormTitle>

            <div className={styles.subtitle}>
              Вход в аккаунт Recipe App
            </div>

            <div className={styles.fields}>
              <Input
                required
                isAuth={true}
                name="email"
                placeholder="Email"
                onChange={onChange}
                error={errors}
              />
              <Input
                required
                isAuth={true}
                type="password"
                name="password"
                placeholder="Пароль"
                error={errors}
                submitError={submitError}
                onChange={onChange}
              />
            </div>

            <Button modifier="style_dark" type="submit" className={styles.button}>
              Войти
            </Button>
          </Form>
        </div>
      </Container>
    </Main>
  );
};

export default SignIn;