<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Verificador de precios con IA</title>
</head>
<body>
    <h2>Verificar errores de precio</h2>

    <form id="form">
        <label>PDF de ofertas</label><br>
        <input type="file" name="pdf" accept=".pdf" required><br><br>

        <label>Excel de precios</label><br>
        <input type="file" name="excel" accept=".xlsx" required><br><br>

        <button type="submit">Verificar</button>
    </form>

    <pre id="resultado"></pre>

    <script>
        const form = document.getElementById("form");
        const resultado = document.getElementById("resultado");

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            resultado.textContent = "Analizando con IA...";

            const formData = new FormData(form);

            try {
                const response = await fetch("/check", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();

                resultado.textContent = data.ok
                    ? data.message
                    : "Error: " + data.error;

            } catch {
                resultado.textContent = "Error de conexión con el servidor";
            }
        });
    </script>
</body>
</html>
