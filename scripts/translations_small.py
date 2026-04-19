"""Manual translations for the small files (Configuration, Module.lstr, ObjectModule, Form, Тесты).

Keyed by relative path under dictionaries_en/src/.
"""

TR = {
    "Configuration/Configuration_en.lstr": {
        "Language.Русский.Synonym": "Russian",
    },

    "Configuration/Configuration_en.trans": {
        "Comment": "Connector\\: handy HTTP-client for 1C\\:Enterprise 8 platform",
    },

    "CommonModules/КоннекторHTTP/Module_en.lstr": {
        "Method.ВырезатьТекст.NStr.<Данные>.Lines":
            "<Data>",
        "Method.ЗаписатьZip.NStr.Работа\\ с\\ Zip-файлами\\ в\\ мобильной\\ платформе\\ не\\ поддерживается.Lines":
            "Zip files are not supported on the mobile platform",
        "Method.КакJson.NStr.Ошибка\\ при\\ десериализации\\ JSON\\..Lines":
            "JSON deserialization error.",
        "Method.КакXDTO.NStr.Ошибка\\ при\\ десериализации\\ XDTO\\..Lines":
            "XDTO deserialization error.",
        "Method.КакИсключение.Var.ТекстИсключения.NStr.Тело\\ ответа\\:\\n%1.Lines":
            "Response body\\:\\n%1",
        "Method.ПредставлениеКодаСостоянияHTTP.NStr.%1\\:\\ Неизвестный\\ код\\ состояния\\ HTTP.Lines":
            "%1\\: Unknown HTTP status code",
        "Method.Приостановить.NStr.Процедура\\ Приостановить\\ не\\ работает\\ должным\\ образом.Lines":
            "Pause procedure does not work as expected",
        "Method.ПрочитатьZip.NStr.Работа\\ с\\ Zip-файлами\\ в\\ мобильной\\ платформе\\ не\\ поддерживается.Lines":
            "Zip files are not supported on the mobile platform",
    },

    "DataProcessors/Тесты/ObjectModule_en.trans": {
        "Method.ВыполнитьТестыНаСервере.Description":
            "Runs the test execution",
        "Method.ПолучитьСписокТестов.Description":
            "Returns the list of tests",
        "Method.Тест_POST_MultipartFormData_ФайлыИПоляФормы_КонструкторПараметров.Comment.Должно\\ быть\\ \"Привет,\\ Мир\".Description":
            "Should be \"Hello, World\"",
    },

    "DataProcessors/Тесты/Forms/Форма/Form_en.lstr": {
        "Attribute.КоличествоТестов.Title":             "Test count",
        "Attribute.Тесты.Title":                        "Tests",
        "Attribute.Тесты.Использование.Title":          "Usage",
        "Attribute.Тесты.Ошибка.Title":                 "Error",
        "Attribute.Тесты.Результат.Title":              "Result",
        "Attribute.Тесты.Тест.Title":                   "Test",
        "Command.ВыполнитьТесты.Title":                 "Run tests",
        "Command.ВыполнитьТесты.ToolTip":               "Run tests",
        "Command.СнятьФлажки.Title":                    "Uncheck all",
        "Command.УстановитьФлажки.Title":               "Check all",
        "Item.Группа1.Title":                           "AWS4-HMAC-SHA256 authentication settings",
        "Item.Группа3.Title":                           "Proxy server settings",
        "Item.Группа4.Title":                           "1C websites authentication settings",
        "Item.ГруппаЛогинПароль.Title":                 "Login and password",
        "Item.ГруппаСерверПорт.Title":                  "Server and port",
        "Item.ПроксиПорт.Title":                        "Port",
        "Item.ПроксиСервер.Title":                      "Server",
        "Item.СтраницаНастройки.Title":                 "Settings",
        "Item.СтраницаТесты.Title":                     "Tests",
        "Item.Страницы.Title":                          "Pages",
        "Item.Страницы.ToolTip":                        "Pages",
    },

    "DataProcessors/Тесты/Тесты_en.lstr": {
        "Attribute.ИдентификаторКлючаДоступа.Synonym":                     "Access key identifier",
        "Attribute.Логин.Synonym":                                         "Login",
        "Attribute.Очередь.Synonym":                                       "Queue",
        "Attribute.Пароль.Synonym":                                        "Password",
        "Attribute.ПроксиПорт.Synonym":                                    "Proxy port",
        "Attribute.ПроксиСервер.Synonym":                                  "Proxy server",
        "Attribute.Регион.Synonym":                                        "Region",
        "Attribute.СекретныйКлюч.Synonym":                                 "Secret key",
        "Attribute.ТестироватьАутентификациюAWS4_HMAC_SHA256.Synonym":     "Test AWS4-HMAC-SHA256 authentication",
        "Attribute.ТестироватьПовторы.Synonym":                            "Test retries",
        "Attribute.ТестироватьПолучениеСпискаРелизовВСайта1С.Synonym":     "Test fetching release list from 1C website",
        "Attribute.ТестироватьСоединениеЧерезПрокси.Synonym":              "Test connection through proxy",
        "Form.Форма.Synonym":                                              "Form",
    },
}
