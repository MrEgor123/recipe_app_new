import cn from "classnames";
import styles from "./style.module.css";

const Button = ({
  children,
  modifier = "style_light",
  href,
  clickHandler,
  className,
  disabled,
  type = "button",
  ...rest
}) => {
  const classNames = cn(styles.button, className, {
    [styles[`button_${modifier}`]]: modifier,
    [styles.button_disabled]: disabled,
  });

  if (href) {
    return (
      <a className={classNames} href={href}>
        {children}
      </a>
    );
  }

  return (
    <button
      type={type}
      className={classNames}
      disabled={disabled}
      onClick={type === "button" ? () => clickHandler && clickHandler() : undefined}
      {...rest}
    >
      {children}
    </button>
  );
};

export default Button;