define(['app/action/attack'], function(Attack) {
	
	var FastAttack = function(options) {
		this.target = options.target;
	};
	FastAttack.prototype = new Attack();
	FastAttack.constructor = FastAttack;
	
	FastAttack.prototype.doFrameAction = function(frame) {
		if(frame == 1 || frame == 3) {
			var hit = this.hitEvent();
			this.target.takeDamage(this._entity.getDamage(), this._entity);
			require('app/eventmanager').trigger(hit);
		}
		if(frame == 3) {
			this._entity.action = null;
		}
	};
	
	return FastAttack;
});