#include <regex>
extern "C" {
    __declspec(dllexport) bool validar_correo_cpp(const char* email) {
        const std::regex pattern(R"((\w+)(\.{1}\w+)*@(\w+)(\.\w+)+)");
        return std::regex_match(email, pattern);
    }
}