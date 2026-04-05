import "./fonts/SanFranciscoProDisplay/fonts.css";
import "./App.css";
import { Switch, Route, useHistory, Redirect } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { Header, Footer, ProtectedRoute } from "./components";
import api from "./api";
import styles from "./styles.module.css";

import {
  Main,
  Cart,
  SignIn,
  Subscriptions,
  Favorites,
  SingleCard,
  SignUp,
  RecipeEdit,
  RecipeCreate,
  User,
  ChangePassword,
  NotFound,
  UpdateAvatar,
  ResetPassword,
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
    };

    return map[raw] || "Не удалось войти. Проверьте введённые данные";
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
        history.push("/signin");
      })
      .catch((err) => {
        const errors = Object.values(err);
        if (errors) {
          setRegistrError({ submitError: errors.join(", ") });
        }
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
      .getShoppingCartCount()
      .then((res) => {
        setOrders(res.count || 0);
      })
      .catch(() => {
        setOrders(0);
      });
  };

  const authorization = ({ email, password }) => {
    api
      .signin({
        email,
        password,
      })
      .then((res) => {
        if (res.auth_token) {
          localStorage.setItem("token", res.auth_token);
          api
            .getUserData()
            .then((res) => {
              setUser(res);
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
      .resetPassword({
        email,
      })
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

  const loadSingleItem = ({ id, callback }) => {
    setTimeout(() => {
      callback();
    }, 3000);
  };

  const onSignOut = () => {
    api
      .signout()
      .then(() => {
        localStorage.removeItem("token");
        setUser({});
        setOrders(0);
        setLoggedIn(false);
        history.push("/recipes");
      })
      .catch(() => {
        localStorage.removeItem("token");
        setUser({});
        setOrders(0);
        setLoggedIn(false);
        history.push("/recipes");
      });
  };

  const updateOrders = (add) => {
    if (!add && orders <= 0) {
      return;
    }
    if (add) {
      setOrders(orders + 1);
    } else {
      setOrders(orders - 1);
    }
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
    } else {
      setLoggedIn(false);
    }
  }, []);

  if (loggedIn === null) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  return (
    <AuthContext.Provider value={loggedIn}>
      <UserContext.Provider value={user}>
        <div className="App">
          <Header orders={orders} loggedIn={loggedIn} onSignOut={onSignOut} />
          <Switch>
            <Route
              exact
              path="/user/:id"
              component={User}
              updateOrders={updateOrders}
            />
            <ProtectedRoute
              exact
              path="/cart"
              component={Cart}
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

            <Route exact path="/about">
              <NotFound />
            </Route>

            <Route exact path="/reset-password">
              <ResetPassword onPasswordReset={onPasswordReset} />
            </Route>

            <Route exact path="/technologies">
              <NotFound />
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
        </div>
      </UserContext.Provider>
    </AuthContext.Provider>
  );
}

export default App;