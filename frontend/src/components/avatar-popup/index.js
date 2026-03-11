import { Icons, Button } from "..";
import DefaultImage from "../../images/avatar-icon.png";
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

export const AvatarPopup = ({
  onSubmit,
  onClose,
  fileSize = 5,
  fileTypes = ["jpg", "png"],
  onChange,
  avatar,
}) => {
  const [currentFile, setCurrentFile] = useState(avatar || null);
  const [error, setError] = useState("");
  const fileInput = useRef(null);

  useEffect(() => {
    setCurrentFile(avatar || null);
  }, [avatar]);

  const getBase64 = (file) => {
    if (!file) return;

    const reader = new FileReader();
    const fileNameArr = file.name.split(".");
    const format = fileNameArr[fileNameArr.length - 1]?.toLowerCase();

    if (fileSize && file.size / (1024 * 1024) > fileSize) {
      return setError(`Загрузите файл размером не более ${fileSize}Мб`);
    }

    if (fileTypes && !fileTypes.includes(format)) {
      return setError(
        `Загрузите файл одного из типов: ${fileTypes.join(", ")}`
      );
    }

    reader.readAsDataURL(file);
    reader.onload = function () {
      setCurrentFile(reader.result);
      onChange(reader.result);
    };
    reader.onerror = function (err) {
      console.log("Error: ", err);
    };
  };

  const popupNode = (
    <div
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose?.();
      }}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        background: "rgba(15,23,42,.22)",
        backdropFilter: "blur(4px)",
      }}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          maxWidth: "420px",
          background: "#fff",
          border: "1px solid #e5e7eb",
          borderRadius: "24px",
          boxShadow: "0 12px 30px rgba(15,23,42,.14)",
          padding: "28px 28px 24px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "flex-start",
        }}
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Закрыть"
          style={{
            position: "absolute",
            top: "12px",
            right: "12px",
            width: "32px",
            height: "32px",
            border: "none",
            background: "transparent",
            borderRadius: "999px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Icons.PopupClose />
        </button>

        <h3
          style={{
            margin: "0 0 18px",
            fontFamily: '"SF Pro Display", sans-serif',
            fontSize: "28px",
            fontWeight: 700,
            lineHeight: 1.2,
            color: "#0f172a",
            textAlign: "center",
          }}
        >
          Аватар
        </h3>

        <div
          style={{
            width: "220px",
            height: "220px",
            borderRadius: "50%",
            overflow: "hidden",
            position: "relative",
            border: "1px solid #e5e7eb",
            background: "#f8fafc",
            flexShrink: 0,
            margin: 0,
          }}
        >
          <img
            src={currentFile || DefaultImage}
            alt="Аватар"
            style={{
              display: "block",
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: "center center",
              margin: 0,
              padding: 0,
            }}
          />

          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "12px",
              background: "rgba(15,23,42,.35)",
            }}
          >
            <button
              type="button"
              onClick={() => fileInput.current?.click()}
              aria-label="Загрузить аватар"
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "999px",
                border: "1px solid rgba(255,255,255,.9)",
                background: "rgba(255,255,255,.14)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                padding: 0,
              }}
            >
              <Icons.AddAvatarIcon />
            </button>

            {currentFile && (
              <button
                type="button"
                onClick={() => {
                  setCurrentFile(null);
                  onChange(null);
                  if (fileInput.current) fileInput.current.value = "";
                }}
                aria-label="Удалить аватар"
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "999px",
                  border: "1px solid rgba(255,255,255,.9)",
                  background: "rgba(255,255,255,.14)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                  padding: 0,
                }}
              >
                <Icons.DeleteAvatarIcon />
              </button>
            )}
          </div>
        </div>

        <input
          type="file"
          ref={fileInput}
          style={{ display: "none" }}
          onChange={(e) => {
            setError("");
            getBase64(e.target.files?.[0]);
          }}
        />

        {error && (
          <p
            style={{
              margin: "14px 0 0",
              fontSize: "14px",
              fontWeight: 600,
              lineHeight: 1.4,
              color: "#ff3b30",
              textAlign: "center",
            }}
          >
            {error}
          </p>
        )}

        <p
          style={{
            margin: "16px 0 0",
            fontSize: "14px",
            fontWeight: 500,
            lineHeight: 1.4,
            color: "#64748b",
            textAlign: "center",
          }}
        >
          {`формат ${fileTypes.join("/")}, размер до ${fileSize}мб`}
        </p>

        <Button
          modifier="style_dark"
          clickHandler={onSubmit}
          style={{
            marginTop: "18px",
            minHeight: "42px",
            padding: "0 20px",
          }}
        >
          Сохранить
        </Button>
      </div>
    </div>
  );

  return createPortal(popupNode, document.body);
};