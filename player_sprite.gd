extends Sprite2D

var startposition = position

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

func _init():
	print("Startup")

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if Input.is_action_pressed("ui_right"):
		rotation += delta * 4;
	elif Input.is_action_pressed("ui_left"):
		rotation += delta * (-4);
	if Input.is_action_pressed("ui_up"):
		position += Vector2.UP.rotated(rotation) * 10

func _on_button_pressed():
	position = startposition
	rotation = 0
