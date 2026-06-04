import {
  Container,
  Input,
  FormTitle,
  Main,
  Form,
  Button,
} from "../../components";
import styles from "./styles.module.css";
import { useFormWithValidation } from "../../utils";
import { Redirect } from "react-router-dom";
import { useContext, useState } from "react";
import { AuthContext } from "../../contexts";
import MetaTags from "react-meta-tags";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const SignUp = ({ onSignUp, submitError, setSubmitError }) => {
  const { values, handleChange, errors } = useFormWithValidation();
  const authContext = useContext(AuthContext);
  const [localError, setLocalError] = useState("");

  const onChange = (e) => {
    setLocalError("");
    setSubmitError({ submitError: "" });
    handleChange(e);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const email = (values.email || "").trim();
    const username = (values.username || "").trim();
    const firstName = (values.first_name || "").trim();
    const lastName = (values.last_name || "").trim();
    const password = values.password || "";

    if (!firstName || !lastName || !username || !email || !password) {
      setLocalError("Заполните все обязательные поля.");
      return;
    }

    if (!EMAIL_RE.test(email)) {
      setLocalError("Введите корректный адрес электронной почты.");
      return;
    }

    if (username.length < 3) {
      setLocalError("Имя пользователя должно содержать не менее 3 символов.");
      return;
    }

    onSignUp({
      ...values,
      email,
      username,
      first_name: firstName,
      last_name: lastName,
    });
  };

  const errorText =
    localError ||
    submitError?.submitError ||
    submitError?.message ||
    "";

  return (
    <Main withBG asFlex>
      {authContext && <Redirect to="/recipes" />}
      <Container className={styles.center}>
        <MetaTags>
          <title>Регистрация</title>
          <meta
            name="description"
            content="Recepto - Регистрация"
          />
          <meta property="og:title" content="Регистрация" />
        </MetaTags>

        <Form className={styles.form} onSubmit={handleSubmit}>
          <FormTitle>Регистрация</FormTitle>

          <Input
            placeholder="Имя"
            name="first_name"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />

          <Input
            placeholder="Фамилия"
            name="last_name"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />

          <Input
            placeholder="Имя пользователя"
            name="username"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />

          <Input
            placeholder="Адрес электронной почты"
            name="email"
            type="email"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />

          <Input
            placeholder="Пароль"
            type="password"
            name="password"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />

          {errorText && (
            <p className={styles.error}>
              {errorText}
            </p>
          )}

          <Button modifier="style_dark" type="submit" className={styles.button}>
            Создать аккаунт
          </Button>
        </Form>
      </Container>
    </Main>
  );
};

export default SignUp;