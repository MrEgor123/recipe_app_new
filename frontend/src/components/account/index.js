import styles from "./styles.module.css";
import { useContext, useMemo, useState } from "react";
import { LinkComponent, Orders } from "../index.js";
import { AuthContext, UserContext } from "../../contexts";
import { UserMenu } from "../../configs/navigation";
import Icons from "../icons";
import DefaultImage from "../../images/userpic-icon.jpg";
import { AvatarPopup } from "../avatar-popup";
import api from "../../api";

const AccountData = ({ userContext }) => {
  const fullName =
    `${userContext.first_name || ""} ${userContext.last_name || ""}`.trim() ||
    userContext.username ||
    "Пользователь";

  return (
    <LinkComponent
      href="/profile"
      className={styles.accountProfileLink}
      title={
        <div className={styles.accountProfile}>
          <div
            style={{
              backgroundImage: `url(${userContext.avatar || DefaultImage})`,
            }}
            className={styles.accountAvatar}
          />
          <div className={styles.accountData}>
            <div className={styles.accountName}>{fullName}</div>
            <div className={styles.accountEmail}>{userContext.email}</div>
          </div>
        </div>
      }
    />
  );
};

const Account = ({ onSignOut, orders }) => {
  const authContext = useContext(AuthContext);
  const userContext = useContext(UserContext);
  const [isChangeAvatarOpen, setIsChangeAvatarOpen] = useState(false);
  const [newAvatar, setNewAvatar] = useState("");

  const menuItems = useMemo(() => {
    return [
      {
        href: "/profile",
        title: "Мой профиль",
        icon: <Icons.UserIcon />,
      },
      ...UserMenu,
    ];
  }, []);

  const handleSaveAvatar = () => {
    if (newAvatar) {
      api
        .changeAvatar({ file: newAvatar })
        .then(({ avatar }) => {
          userContext.avatar = avatar;
          setIsChangeAvatarOpen(false);
        })
        .catch((err) => console.log(err));
    } else {
      api
        .deleteAvatar()
        .then(() => {
          userContext.avatar = "";
          setIsChangeAvatarOpen(false);
        })
        .catch((err) => console.log(err));
    }
  };

  if (!authContext) {
    return null;
  }

  return (
    <>
      <LinkComponent
        className={styles.accountOrders}
        href="/cart"
        title={<Orders orders={orders} />}
      />

      <div className={styles.account}>
        <div className={styles.accountTrigger}>
          <AccountData userContext={userContext} />
          <button
            type="button"
            className={styles.accountAvatarEditBtn}
            onClick={() => {
              setIsChangeAvatarOpen(true);
            }}
            aria-label="Изменить аватар"
            title="Изменить аватар"
          >
            <Icons.AddAvatarIcon />
          </button>
        </div>

        <div className={styles.accountControls}>
          <ul className={styles.accountLinks}>
            {menuItems.map((menuItem) => {
              return (
                <li key={menuItem.href} className={styles.accountLinkItem}>
                  <LinkComponent
                    className={styles.accountLink}
                    href={menuItem.href}
                    title={
                      <div className={styles.accountLinkTitle}>
                        <div className={styles.accountLinkIcon}>
                          {menuItem.icon}
                        </div>
                        {menuItem.title}
                      </div>
                    }
                  />
                </li>
              );
            })}

            <li className={styles.accountLinkItem} onClick={onSignOut}>
              <div className={styles.accountLinkTitle}>
                <div className={styles.accountLinkIcon}>
                  <Icons.LogoutMenu />
                </div>
                Выйти
              </div>
            </li>
          </ul>
        </div>
      </div>

      {isChangeAvatarOpen && (
        <AvatarPopup
          info="test"
          avatar={userContext.avatar}
          onClose={() => setIsChangeAvatarOpen(false)}
          onSubmit={handleSaveAvatar}
          onChange={setNewAvatar}
        />
      )}
    </>
  );
};

export default Account;