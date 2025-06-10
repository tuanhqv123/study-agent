import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const checkSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (data?.session) {
        const { user } = data.session;
        const { data: userData } = await supabase
          .from("public_users")
          .select("user_role")
          .eq("id", user.id)
          .single();
        if (userData?.user_role?.trim().toLowerCase() === "admin") {
          navigate("/admin");
        } else {
          navigate("/chat");
        }
      } else {
        navigate("/login");
      }
    };
    checkSession();
  }, [navigate]);

  return <div>Đang xác thực...</div>;
};

export default AuthCallback;
