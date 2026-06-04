import "./fonts/SanFranciscoProDisplay/fonts.css";
import "./App.css";
import { Switch, Route, useHistory, Redirect } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { Header, Footer, ProtectedRoute } from "./components";
import api from "./api";
import styles from "./styles.module.css";

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import {
  Main,
  SignIn,
  Subscriptions,
  Favorites,
  SingleCard,
  SignUp,
  RecipeEdit,
  RecipeCreate,
  ChangePassword,
  NotFound,
  UpdateAvatar,
  ResetPassword,
  ProfilePage,
  ProfileEditPage,
  CollectionDetailPage,
  ShoppingCartPage,
} from "./pages";

import { AuthContext, UserContext } from "./contexts";

function App() {
  const [loggedIn, setLoggedIn] = useState(null);
  const [user, setUser] = useState({});
  const [orders, setOrders] = useState(0);
  const [authError, setAuthError] = useState({ submitError: "" });
  const [registrError, setRegistrError] = useState({ submitError: "" });
  const [changePasswordError, setChangePasswordError] = useState({
    submitError: "",
  });

  const history = useHistory();

  const translateAuthError = (err) => {
    const raw = Object.values(err || {}).flat().join(", ");

    const map = {
      "Unable to log in with provided credentials":
        "Неверные данные для входа. Проверьте email и пароль",
      "Unable to log in with provided credentials.":
        "Неверные данные для входа. Проверьте email и пароль",
      "No active account found with the given credentials":
        "Аккаунт с такими данными не найден",
      "This field may not be blank.": "Поле не должно быть пустым",
      "This field is required.": "Обязательное поле",
      "Invalid token.": "Ошибка авторизации. Войдите в аккаунт заново",
      "Invalid Token": "Ошибка авторизации. Войдите в аккаунт заново",
    };

    return map[raw] || "Не удалось войти. Проверьте введённые данные";
  };

  const getRegistrationErrorMessage = (err) => {
    const fieldNames = {
      email: "Email",
      username: "Имя пользователя",
      password: "Пароль",
      first_name: "Имя",
      last_name: "Фамилия",
      non_field_errors: "Ошибка",
      detail: "Ошибка",
    };

    const translateMessage = (message) => {
      const raw = String(message || "").trim();

      const map = {
        "A user with that username already exists.":
          "Пользователь с таким именем уже существует.",
        "user with this username already exists.":
          "Пользователь с таким именем уже существует.",
        "User with this username already exists.":
          "Пользователь с таким именем уже существует.",
        "Пользователь с таким именем уже существует.":
          "Пользователь с таким именем уже существует.",
        "Enter a valid email address.":
          "Введите корректный адрес электронной почты.",
        "Invalid email.":
          "Введите корректный адрес электронной почты.",
        "This field may not be blank.":
          "Поле не должно быть пустым.",
        "This field is required.":
          "Обязательное поле.",
        "This password is too short.":
          "Пароль слишком короткий.",
        "Invalid token.":
          "Ошибка авторизации. Войдите в аккаунт заново.",
        "Invalid Token":
          "Ошибка авторизации. Войдите в аккаунт заново.",
      };

      if (map[raw]) {
        return map[raw];
      }

      if (raw.includes("already exists")) {
        return "Пользователь с такими данными уже существует.";
      }

      if (raw.includes("valid email")) {
        return "Введите корректный адрес электронной почты.";
      }

      if (raw === "400" || raw === "Bad Request") {
        return "";
      }

      return raw;
    };

    if (!err) {
      return "Не удалось создать аккаунт. Проверьте введённые данные.";
    }

    if (typeof err === "string") {
      return (
        translateMessage(err) ||
        "Не удалось создать аккаунт. Проверьте введённые данные."
      );
    }

    if (Array.isArray(err)) {
      const messages = err.map(translateMessage).filter(Boolean);
      return [...new Set(messages)].join(" ");
    }

    if (typeof err === "object") {
      const messages = [];

      Object.entries(err).forEach(([field, value]) => {
        const values = Array.isArray(value) ? value : [value];

        values.forEach((item) => {
          const text = translateMessage(item);

          if (!text) {
            return;
          }

          if (
            field === "username" &&
            text.includes("Пользователь с таким именем")
          ) {
            messages.push(text);
            return;
          }

          if (field === "email" && text.includes("электронной почты")) {
            messages.push(text);
            return;
          }

          const fieldLabel = fieldNames[field];

          if (fieldLabel && field !== "non_field_errors" && field !== "detail") {
            messages.push(`${fieldLabel}: ${text}`);
          } else {
            messages.push(text);
          }
        });
      });

      const uniqueMessages = [...new Set(messages)];

      if (uniqueMessages.length > 0) {
        return uniqueMessages.join(" ");
      }
    }

    return "Не удалось создать аккаунт. Проверьте введённые данные.";
  };

  const registration = ({
    email,
    password,
    username,
    first_name,
    last_name,
  }) => {
    api
      .signup({ email, password, username, first_name, last_name })
      .then(() => {
        setRegistrError({ submitError: "" });
        history.push("/signin");
      })
      .catch((err) => {
        setRegistrError({
          submitError: getRegistrationErrorMessage(err),
        });
        setLoggedIn(false);
      });
  };

  const changePassword = ({ new_password, current_password }) => {
    api
      .changePassword({ new_password, current_password })
      .then(() => {
        history.push("/signin");
      })
      .catch((err) => {
        const errors = Object.values(err);
        if (errors) {
          setChangePasswordError({ submitError: errors.join(", ") });
        }
      });
  };

  const changeAvatar = ({ file }) => {
    api
      .changeAvatar({ file })
      .then((res) => {
        setUser({ ...user, avatar: res.avatar });
        history.push("/recipes");
      })
      .catch((err) => {
        const { non_field_errors } = err;
        if (non_field_errors) {
          return alert(non_field_errors.join(", "));
        }

        const errors = Object.values(err);
        if (errors) {
          alert(errors.join(", "));
        }
      });
  };

  const getOrders = () => {
    api
      .getRecipes({
        page: 1,
        limit: 999,
        is_in_shopping_cart: 1,
      })
      .then((res) => {
        setOrders(res.count || 0);
      })
      .catch(() => {
        setOrders(0);
      });
  };

  const authorization = ({ email, password }) => {
    api
      .signin({ email, password })
      .then((res) => {
        if (res.auth_token) {
          localStorage.setItem("token", res.auth_token);

          api
            .getUserData()
            .then((userRes) => {
              setUser(userRes);
              setLoggedIn(true);
              getOrders();
            })
            .catch(() => {
              setLoggedIn(false);
              history.push("/signin");
            });
        } else {
          setLoggedIn(false);
        }
      })
      .catch((err) => {
        setAuthError({
          submitError: translateAuthError(err),
        });
        setLoggedIn(false);
      });
  };

  const onPasswordReset = ({ email }) => {
    api
      .resetPassword({ email })
      .then(() => {
        history.push("/signin");
      })
      .catch((err) => {
        const errors = Object.values(err);
        if (errors) {
          alert(errors.join(", "));
        }
        setLoggedIn(false);
      });
  };

  const loadSingleItem = ({ callback }) => {
    setTimeout(() => {
      callback();
    }, 3000);
  };

  const onSignOut = () => {
    api.signout().finally(() => {
      localStorage.removeItem("token");
      setUser({});
      setOrders(0);
      setLoggedIn(false);
      history.push("/recipes");
    });
  };

  const updateOrders = (add) => {
    if (!add && orders <= 0) return;
    setOrders(add ? orders + 1 : orders - 1);
  };

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      return api
        .getUserData()
        .then((res) => {
          setUser(res);
          setLoggedIn(true);
          getOrders();
        })
        .catch(() => {
          setLoggedIn(false);
          history.push("/recipes");
        });
    }

    setLoggedIn(false);
  }, [history]);

  if (loggedIn === null) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  return (
    <AuthContext.Provider value={loggedIn}>
      <UserContext.Provider value={user}>
        <div className="App">
          <Header orders={orders} loggedIn={loggedIn} onSignOut={onSignOut} />

          <Switch>
            <ProtectedRoute
              exact
              path="/profile"
              component={() => <ProfilePage isMe />}
              loggedIn={loggedIn}
            />

            <ProtectedRoute
              exact
              path="/profile/edit"
              component={ProfileEditPage}
              loggedIn={loggedIn}
            />

            <Route exact path="/users/:id">
              <ProfilePage />
            </Route>

            <Route exact path="/collection/:id">
              <CollectionDetailPage />
            </Route>

            <Route exact path="/collections/:id">
              <CollectionDetailPage />
            </Route>

            <ProtectedRoute
              exact
              path="/cart"
              component={ShoppingCartPage}
              orders={orders}
              loggedIn={loggedIn}
              updateOrders={updateOrders}
            />

            <ProtectedRoute
              exact
              path="/subscriptions"
              component={Subscriptions}
              loggedIn={loggedIn}
            />

            <ProtectedRoute
              exact
              path="/favorites"
              component={Favorites}
              loggedIn={loggedIn}
              updateOrders={updateOrders}
            />

            <ProtectedRoute
              exact
              path="/recipes/create"
              component={RecipeCreate}
              loggedIn={loggedIn}
            />

            <ProtectedRoute
              exact
              path="/recipes/:id/edit"
              component={RecipeEdit}
              loggedIn={loggedIn}
              loadItem={loadSingleItem}
              onItemDelete={getOrders}
            />

            <ProtectedRoute
              exact
              path="/change-password"
              component={ChangePassword}
              loggedIn={loggedIn}
              submitError={changePasswordError}
              setSubmitError={setChangePasswordError}
              onPasswordChange={changePassword}
            />

            <ProtectedRoute
              exact
              path="/change-avatar"
              component={UpdateAvatar}
              loggedIn={loggedIn}
              onAvatarChange={changeAvatar}
            />

            <Route exact path="/recipes/:id">
              <SingleCard
                loggedIn={loggedIn}
                loadItem={loadSingleItem}
                updateOrders={updateOrders}
              />
            </Route>

            <Route exact path="/reset-password">
              <ResetPassword onPasswordReset={onPasswordReset} />
            </Route>

            <Route exact path="/recipes">
              <Main updateOrders={updateOrders} />
            </Route>

            <Route exact path="/signin">
              <SignIn
                onSignIn={authorization}
                submitError={authError}
                setSubmitError={setAuthError}
              />
            </Route>

            <Route exact path="/signup">
              <SignUp
                onSignUp={registration}
                submitError={registrError}
                setSubmitError={setRegistrError}
              />
            </Route>

            <Route exact path="/">
              <Redirect to="/recipes" />
            </Route>

            <Route path="*">
              <NotFound />
            </Route>
          </Switch>

          <Footer />

          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar={false}
          />
        </div>
      </UserContext.Provider>
    </AuthContext.Provider>
  );
}

export default App;